# todo 1. 对于查询的持仓，空的也要推送空的，否则orderplit无法回调.  这对于http请求很容易实现，但是如果是websocket回调，也许空的不会回调？例如ibk

import pandas as pd
from pandas import DataFrame
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from ks_trade_api.base_fundamental_api import BaseFundamentalApi
from ks_trade_api.utility import extract_vt_symbol, generate_vt_symbol
from ks_trade_api.constant import Exchange, SubExchange, RET_OK, RET_ERROR, Product, RetCode
from ks_utility.datetimes import get_date_str
from ks_utility import datetimes
from ks_utility.datetimes import DATE_FMT
import sys
from decimal import Decimal
import uuid
from logging import DEBUG, WARNING, ERROR
from ks_utility.numbers import to_decimal
from enum import Enum
import traceback
import pandas as pd
import numpy as np
import typing
import re

from .EmQuantAPI import c

class Params(Enum):
    # 下面是我们的参数
    MRYN = 'MRYN' # MRY的N值
    
    # 下面是东财的标准参数
    N = 'N'
    ReportDate = 'ReportDate'
    TradeDate = 'TradeDate'
    Year = 'Year'
    PayYear = 'PayYear'
    IsPandas = 'IsPandas'
    Type = 'Type'
    CurType = 'CurType'
    TtmType = 'TtmType'
    
# 我们的标准字段
class Indicator(Enum):
    ROE = 'ROE' # 净资产收益率
    ROA = 'ROA' # 总资产收益率
    LIBILITYTOASSET = 'LIBILITYTOASSET' # 资产负债率
    DIVANNUPAYRATE = 'DIVANNUPAYRATE' # 年度胜利支付率
    MV = 'MV' # 总市值
    CIRCULATEMV = 'CIRCULATEMV' # 流通市值
    PE = 'PE' # 市盈率
    PB = 'PB' # 市净率
    YOYOR = 'YOYOR' # 营业收入同比增长率(Year-over-Year Operating Revenue)
    YOYNI = 'YOYNI' # 净利润同步增长率(Year-over-Year Net Income)
    CAGRTOR = 'CAGRTOR' # 营业总收入复合增长率(Compound Annual Growth Rate Total Operating revenue)
    GPMARGIN = 'GPMARGIN' # 毛利率
    NPMARGIN= 'NPMARGIN' # 净利率
    
    # 财务报表-现金流量表
    CASHFLOWSTATEMENT_NCFO = 'CASHFLOWSTATEMENT_NCFO' # 经营活动产生的现金流量净额

class MyCurrency(Enum):
    CNY = 2
    USD = 3
    HKD = 4

class MyExchange(Enum):
    SH = 'SH'
    SZ = 'SZ'
    HK = 'HK'
    BJ = 'BJ'

    N = 'N'
    O = 'O'
    A = 'A'
    F = 'F'

EXCHANGE2MY_CURRENCY = {
    Exchange.SSE: MyCurrency.CNY,
    Exchange.SZSE: MyCurrency.CNY,
    Exchange.BSE: MyCurrency.CNY,
    Exchange.SEHK: MyCurrency.HKD,
    Exchange.SMART: MyCurrency.USD
}

EXCHANGE_KS2MY = {
    Exchange.SSE: MyExchange.SH,
    Exchange.SZSE: MyExchange.SZ,
    Exchange.SEHK: MyExchange.HK,
    Exchange.BSE: MyExchange.BJ
}
EXCHANGE_MY2KS = {v:k for k,v in EXCHANGE_KS2MY.items()}
EXCHANGE_MY2KS[MyExchange.A] = Exchange.SMART
EXCHANGE_MY2KS[MyExchange.O] = Exchange.SMART
EXCHANGE_MY2KS[MyExchange.N] = Exchange.SMART
EXCHANGE_MY2KS[MyExchange.F] = Exchange.SMART

EXCHANGE_MY2KS_SUB = {
    MyExchange.A: SubExchange.US_AMEX,
    MyExchange.O: SubExchange.US_NASDAQ,
    MyExchange.N: SubExchange.US_NYSE,
    MyExchange.F: SubExchange.US_PINK,

    MyExchange.SH: SubExchange.CN_SH,
    MyExchange.SZ: SubExchange.CN_SZ,
    MyExchange.BJ: SubExchange.CN_BJ,

    MyExchange.HK: SubExchange.HK_MAINBOARD
}

EXCHANGE_KS2MY_SUB = {v:k for k,v in EXCHANGE_MY2KS_SUB.items()}
EXCHANGE_KS2MY_SUB[SubExchange.CN_STIB] = MyExchange.SH
EXCHANGE_KS2MY_SUB[SubExchange.HK_GEMBOARD] = MyExchange.HK
EXCHANGE_KS2MY_SUB[SubExchange.HK_HKEX] = MyExchange.HK
EXCHANGE_KS2MY_SUB[SubExchange.HK_MAINBOARD] = MyExchange.HK

PERCENT_COLUMNS = ['ROE', 'ROETTM', 'DIVIDENDTTM', 'DIVIDENDYIELDY', 'PE', 'PB']

# 标准字段映射为东财字段(只有需要映射才需要定义，例如ROA就是对应ROA，不需映射)
INDICATORS_KS2MY = {
    # ROE (chice面板上，沪深股票是ROEWA；港股是ROEAVG)
    'ROE.SSE': 'ROEAVG',
    'ROE.SZSE': 'ROEAVG',
    'ROE.BSE': 'ROEAVG',
    'ROE.SEHK': 'ROEAVG',
    'ROE.SMART': 'ROEAVG',
    
    'LIBILITYTOASSET.SSE': 'LIBILITYTOASSETRPT',
    'LIBILITYTOASSET.SZSE': 'LIBILITYTOASSETRPT',
    'LIBILITYTOASSET.BSE': 'LIBILITYTOASSETRPT',
    'LIBILITYTOASSET.SEHK': 'LIBILITYTOASSET',
    'LIBILITYTOASSET.SMART': 'LIBILITYTOASSET',

    'DIVANNUPAYRATE.SSE': 'DIVANNUPAYRATE',
    'DIVANNUPAYRATE.SZSE': 'DIVANNUPAYRATE',
    'DIVANNUPAYRATE.BSE': 'DIVANNUPAYRATE',
    'DIVANNUPAYRATE.SEHK': 'DIVANNUACCUMRATIO',
    'DIVANNUPAYRATE.SMART': 'DIVANNUACCUMRATIO',

    'MV.SSE': 'MV',
    'MV.SZSE': 'MV',
    'MV.BSE': 'MV',
    'MV.SEHK': 'MV',
    'MV.SMART': 'MV',
    
    'CIRCULATEMV.SSE': 'CIRCULATEMV',
    'CIRCULATEMV.SZSE': 'CIRCULATEMV',
    'CIRCULATEMV.BSE': 'CIRCULATEMV',
    'CIRCULATEMV.SEHK': 'LIQMV',
    'CIRCULATEMV.SMART': 'LIQMV',

    'PE.SSE': 'PELYR',
    'PE.SZSE': 'PELYR',
    'PE.BSE': 'PELYR',
    'PE.SEHK': 'PELYR',
    'PE.SMART': 'PELYR',

    'PB.SSE': 'PBMRQ',
    'PB.SZSE': 'PBMRQ',
    'PB.BSE': 'PBMRQ',
    'PB.SEHK': 'PBMRQ',
    'PB.SMART': 'PBMRQ',
    
    'YOYOR.SSE': 'YOYOR',
    'YOYOR.SZSE': 'YOYOR',
    'YOYOR.BSE': 'YOYOR',
    'YOYOR.SEHK': 'GR1YGROWTHRATE',
    'YOYOR.SMART': 'GR1YGROWTHRATE',
    
    'CAGRTOR.SSE': 'CAGRGR',
    'CAGRTOR.SZSE': 'CAGRGR',
    'CAGRTOR.BSE': 'CAGRGR',
    'CAGRTOR.SEHK': 'CAGRGR',
    'CAGRTOR.SMART': 'CAGRGR',
    
    'CASHFLOWSTATEMENT_NCFO.SSE': 'CASHFLOWSTATEMENT_39',
    'CASHFLOWSTATEMENT_NCFO.SZSE': 'CASHFLOWSTATEMENT_39',
    'CASHFLOWSTATEMENT_NCFO.BSE': 'CASHFLOWSTATEMENT_39',
    'CASHFLOWSTATEMENT_NCFO.SEHK': 'CASHFLOWSTATEMENT',
    'CASHFLOWSTATEMENT_NCFO.SMART': 'CASHFLOWSTATEMENT'
}

INDICATORS_MY2KS = {v:'.'.join(k.split('.')[:-1]) for k,v in INDICATORS_KS2MY.items()}

EXCHANGE_PRODUCT2PUKEYCODE = {
    'CNSE.EQUITY': '001071',
    'SEHK.EQUITY': '401001',
    'SMART.EQUITY': '202001004',

    'CNSE.ETF': '507001',
    'SEHK.ETF': '404004',
    'SMART.ETF': '202003009'
}

STATEMENT_EXCHANGE2ITEMS_CODE = {
    'CASHFLOWSTATEMENT.SEHK': 39,
    'CASHFLOWSTATEMENT.SMART': 28
}

def extract_my_symbol(my_symbol):
    items = my_symbol.split(".")
    return '.'.join(items[:-1]), MyExchange(items[-1])

def symbol_ks2my(vt_symbol: str, sub_exchange: SubExchange = None):
    if not vt_symbol:
        return ''
    symbol, ks_exchange = extract_vt_symbol(vt_symbol)
    symbol = symbol.replace('.', '_')
    if not sub_exchange:
        my_symbol = generate_vt_symbol(symbol, EXCHANGE_KS2MY.get(ks_exchange))
    else:
        my_symbol = generate_vt_symbol(symbol, EXCHANGE_KS2MY_SUB.get(sub_exchange))
    return my_symbol

def symbol_my2ks(my_symbol: str):
    if not my_symbol:
        return ''
    symbol, my_exchange = extract_my_symbol(my_symbol)
    symbol = symbol.replace('_', '.') # 东财使用下划线，而我们根据futu的用了.
    return generate_vt_symbol(symbol, EXCHANGE_MY2KS.get(my_exchange))

def symbol_my2sub_exchange(my_symbol: str):
    if not my_symbol:
        return ''
    symbol, my_exchange = extract_my_symbol(my_symbol)
    try:
        EXCHANGE_MY2KS_SUB.get(my_exchange).value
    except:
        breakpoint()
    return EXCHANGE_MY2KS_SUB.get(my_exchange).value

# 用于mry，把为None的数据剔除，并且补齐性质
def clean_group(indicators: list[str] = [], n: int = 3):
    def fn(group):
        cleaned = pd.DataFrame()
        for col in group.columns:
            if col in indicators:
                # 把开头和结尾的空值都给去掉
                s = group[col].fillna(np.nan)
                start = s.first_valid_index()
                end = s.last_valid_index()
                non_na = s.loc[start:end]
                # 这里是因为某些指标没有制定日期的数据会往前滚动取数，所以导致重复，所以删除头两行一致的其中一行
                non_na = non_na.drop([x for x in non_na.duplicated()[lambda x: x].index if x < 2]) 
                series = non_na.reset_index(drop=True)
                series = series.reindex(range(len(group)))
                cleaned[col] = series
            else:
                cleaned[col] = group[col].reset_index(drop=True)
        return cleaned.head(n)
    return fn


class KsEastmoneyFundamentalApi(BaseFundamentalApi):
    gateway_name: str = "KS_EASTMONEY_FUNDAMENTAL"

    def __init__(self, setting: dict):
        dd_secret = setting.get('dd_secret')
        dd_token = setting.get('dd_token')
        gateway_name = setting.get('gateway_name', self.gateway_name)
        super().__init__(gateway_name=gateway_name, dd_secret=dd_secret, dd_token=dd_token)

        self.setting = setting
        self.login()

    def login(self):
        username = self.setting.get('username')
        password = self.setting.get('password')
        startoptions = "ForceLogin=1" + ",UserName=" + username + ",Password=" + password;
        loginResult = c.start(startoptions, '')
        self.log(loginResult, '登录结果')

    def _normalization_indicators_input(self, indicators: str, exchange: Exchange):
        indicators_list = indicators.split(',')
        indicators_new = [INDICATORS_KS2MY.get(f'{x}.{exchange.value}', x) for x in indicators_list]
        return ','.join(indicators_new)
    
    def _normalization_indicators_output(self, df: DataFrame):
        rename_columns = {x:INDICATORS_MY2KS[x] for x in df.columns if x in INDICATORS_MY2KS}
        return df.rename(columns=rename_columns)

    # 暂时不支持跨市场多标的，使用第一个表的市场来决定所有标的的市场
    # sub_exchange是用来做美股区分，东财
    def css(self, vt_symbols: list[str], indicators: str = '', options: str = '', sub_exchanges: list[str] = []) -> tuple[RetCode, pd.DataFrame]:
        if not vt_symbols:
            return None
        
        symbol, exchange = extract_vt_symbol(vt_symbols[0])
        
        indicators = self._normalization_indicators_input(indicators, exchange)

        # 默认pandas返回
        if not 'IsPandas' in options:
            options += ',IsPandas=1'

        if not 'TradeDate' in options:
            options += f',TradeDate={get_date_str()}'
        
        if not 'N=' in options: # CAGRTOR需要N参数
            options += ',N=3'    

        year = datetimes.now().year
        if not 'Year' in options:      
            options += f',Year={year}'

        if not 'PayYear' in options:
            options += f',PayYear={year}'

        if not 'ReportDate' in options:
            options += ',ReportDate=MRQ'

        if not 'CurType' in options:
            # options += f',CurType={EXCHANGE2MY_CURRENCY.get(exchange).value}'
            options += f',CurType=1' # 使用原始币种，港股-人民币

        if 'ROETTM' in indicators:
            options += ',TtmType=1'

        if 'LIBILITYTOASSETRPT' in indicators:
            options += ',Type=3' # 合并报表（调整后）
            
        if 'STATEMENT' in indicators:
            statement_matched = re.search(r'([^,]+STATEMENT\b)', indicators)
            if statement_matched:
                statement_indicator = statement_matched.groups()[0]
                ItemsCode = STATEMENT_EXCHANGE2ITEMS_CODE.get(f'{statement_indicator}.{exchange.value}')
                options += f',ItemsCode={ItemsCode}' # 合并报表（调整后）

        # if 'BPS' in indicators:
        #     options += f',CurType={EXCHANGE2MY_CURRENCY.get(exchange).value}'

        my_symbols = [symbol_ks2my(x, SubExchange(sub_exchanges[i]) if len(sub_exchanges) and sub_exchanges[i] else None) for i,x in enumerate(vt_symbols)]
        df = c.css(my_symbols, indicators=indicators, options=options)
        if isinstance(df, c.EmQuantData):
            return RET_ERROR, str(df)
        
        df.reset_index(drop=False, inplace=True)

        # 转换symbol
        df['CODES'] = df['CODES'].transform(symbol_my2ks)
        df.rename(columns={'CODES': 'vt_symbol'}, inplace=True)

        # LIBILITYTOASSET: 港美的是百分号，A股是小数
        if 'LIBILITYTOASSET' in df.columns:
            is_cn = df.vt_symbol.str.endswith('.SSE') | df.vt_symbol.str.endswith('.SZSE') | df.vt_symbol.str.endswith('.CNSE')
            df.loc[is_cn, 'LIBILITYTOASSET'] = df[is_cn]['LIBILITYTOASSET'] * 100

        df = self._normalization_indicators_output(df)

        # 转换百分比 # 20241223不再转换百分比，因为约定俗称就是用百分比
        # for column in PERCENT_COLUMNS:
        #     if column in df.columns:
        #         df[column] = df[column] / 100

        return RET_OK, df
    
    # alisa放阿飞
    css_mrq = css
    
    def _parse_options(self, options: str = '') -> dict:
        ret_options = {}
        for k,v in dict(x.strip().split('=') for x in options.split(',')).items():
            try:
                enumn_key = Params(k)
            except Exception as e:
                raise e
            ret_options[enumn_key] = v if not v.isdigit() else int(v)
        return ret_options
    
    def _generate_options(self, options: dict = {}) -> str:
        return ','.join([f'{k.name if isinstance(k, Enum) else k}={v}' for k,v in options.items()])
    
    def _parse_indicators(self, indicators: str = '', typing: typing = Enum) -> dict:
        ret_indicators = []
        for k in [x.strip() for x in indicators.split(',')]:
            if typing == str:
                key = k
            else:
                try:
                    key = Indicator(k)
                except Exception as e:
                    raise e
            ret_indicators.append(key)
        return ret_indicators
    
    def _generate_indicators(self, indicators: dict = {}) -> str:
        return ','.join([x.name if isinstance(x, Enum) else x for x in indicators])
    
    # 获取最近N年的数据例如2024-12-31, 2023-12-31, 2022-12-31
    def css_mry(self, vt_symbols: list[str], indicators: str = '', options: str = '', sub_exchanges: list[str] = []) -> pd.DataFrame:
        try:
            options = self._parse_options(options)
            n = options[Params.MRYN]
            
            # 因为年报公布延迟，年初的时候没有当年和前一年的数据，所以要取N个数据必须是N+2年
            y0 = datetimes.now().replace(month=12, day=31)
            dates = [(y0-relativedelta(years=i)).strftime(DATE_FMT) for i in range(n+2)]
            del options[Params.MRYN]
            all_df = pd.DataFrame()
            for date in dates:
                options[Params.ReportDate] = date
                year = date[:4]
                options[Params.Year] = year
                options[Params.PayYear] = year
                other_options = self._generate_options(options)
                ret, df = self.css(
                    vt_symbols=vt_symbols,
                    indicators=indicators,
                    options=other_options,
                    sub_exchanges=sub_exchanges
                )
                if ret == RET_ERROR:
                    return RET_ERROR, df
                df['DATES'] = date
                all_df = pd.concat([all_df, df], ignore_index=True)

            indicators_str = self._parse_indicators(indicators, typing=str)
            cleaned = all_df.groupby('vt_symbol', group_keys=False).apply(clean_group(indicators=indicators_str, n=n))
            table = cleaned.reset_index(drop=False).pivot(index='vt_symbol', columns='index', values=indicators_str)
            table.columns = [f"{col[0]}_MRY{col[1]}" for col in table.columns]
            table = table.loc[vt_symbols] # 按照传入的顺序组织顺组，因为pivot把顺序弄乱了
            table.reset_index(drop=False, inplace=True)
            table
            return RET_OK, table
                
            
        except Exception as e:
            return RET_ERROR, traceback.format_exc()
    
    def sector(self, exchange: Exchange, products: list[Product], tradedate: str = None):
        if not tradedate:
            tradedate = get_date_str()
        # 默认pandas返回
        options = 'IsPandas=1'

        all_df = pd.DataFrame()
        for product in products:
            pukeycode = EXCHANGE_PRODUCT2PUKEYCODE.get(f'{exchange.name}.{product.name}')
            df = c.sector(pukeycode, tradedate, options)
            df['vt_symbol'] = df['SECUCODE'].transform(symbol_my2ks)
            df['sub_exchange'] = df['SECUCODE'].transform(symbol_my2sub_exchange)
            df['name'] = df['SECURITYSHORTNAME']
            df['product'] = product.name

            all_df = pd.concat([all_df, df[['vt_symbol', 'name', 'sub_exchange', 'product']]], ignore_index=True)
        return RET_OK, all_df

    # 关闭上下文连接
    def close(self):
        pass
        # self.quote_ctx.close()
        # self.trd_ctx.close()


        