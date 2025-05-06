from mcp.server.fastmcp import FastMCP
import tushare as ts
from datetime import datetime
import os
import pandas as pd
import tempfile
import base64
import io
import mplfinance as mpf

tushare_mcp = FastMCP("tushare-mcp")

@tushare_mcp.tool()
def today() -> str:
    """
        获取今天日期
    Returns:
        str: 返回YYYYMMDD格式的日期
    """
    return datetime.now().strftime('%Y%m%d') 

@tushare_mcp.tool()
def plot_daily_candlestick_chart(
    ts_code: str,
    start_date: str = '',
    end_date:   str = ''
) -> str:
    """
    根据指定的TS股票代码, 起止时间绘制日线蜡烛图, 并返回蜡烛图文件保存的本地地址
    Args:
        ts_code: TS股票代码
        start_date: 要绘制的开始时间段. 格式为: YYYYMMDD. 示例: 20240430. 默认传入空串, 则绘制所有时间段数据.
        end_date: 要绘制的结束时间段, 格式为: YYYYMMDD. 示例: 20240530. 默认传入空串, 则绘制所有时间段数据.
    Returns:
        str: 图片路径
    """
    # 查询数据
    params = {
        'ts_code': ts_code
    }
    if(start_date != ""):
        params["start_date"] = start_date
    if(end_date != ""):
        params["end_date"] = end_date

    df = ts.pro_api(TUSHARE_API_TOKEN).daily(**params)
   
    # 确保 trade_date 列被正确解析为日期格式
    try:
        df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        # 将 trade_date 列设置为索引
        df.set_index('trade_date', inplace=True)
        # 检查是否包含所需的列
        required_columns = ['open', 'high', 'low', 'close']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Missing required columns in the data.")
        # 准备OHLC数据
        ohlc = df[required_columns].copy()
        if ohlc.empty:
            raise ValueError("No data available to plot.")
        
        # 创建一个临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_image_file:
            # 生成图像并保存到临时文件
            mpf.plot(ohlc, type='candle', style='charles', title='Candlestick Chart of 688230.SH', ylabel='Price', savefig=temp_image_file.name)
            
            # 返回临时文件的路径
            return temp_image_file.name
    except Exception as e:
        raise ValueError(f"Error processing data for candlestick chart: {e}")

@tushare_mcp.tool()
def weekly(
    ts_code:    str = '',
    trade_date: str = '',
    start_date: str = '',
    end_date:   str = '',
    offset:     int = -1,
    limit:      int = -1
) -> str:
    """
    用于查询周维度的交易信息.
    两种用法:
        用法1: 查询指定时间段内,指定股票代码的所有周维度交易信息. 需传入一下三个参数:ts_code, start_date, end_date
        用法2, 查询指定股票代码的所有交易信息, 需传入:ts_code, 其他参数保持默认值
        用法3: 查询某个交易日,所有股票的交易信息. 需传入一下参数: trade_date, 其他参数保持默认值
        用法4: 查询所有股票的所有交易信息, 所有参数保持默认值
    Args:
        ts_code: TS股票代码
        trade_date: 当要查询某个交易日所有股票交易信息时,传入该参数. 格式为: YYYYMMDD. 示例: 20240430
        start_date: 查询开始时间段. 格式为: YYYYMMDD. 示例: 20240430. 传入空串, 则不限制查询时间段.
        end_date: 查询结束时间段. 格式为: YYYYMMDD.  示例: 20240430. 传入空串, 则不限制查询时间段.
        offset: 返回数据的开始行数. 主要用于分批次查询. 传入-1时, 默认查询所有数据.
        limit: 本次返回的数据量. 主要用于分批次查询. 传入-1时, 默认查询所有数据.
    Returns:
        str : 交易信息, 第一行为列名, 之后为数据行, 每列用逗号分隔
              包含如下列, 列类型如下,  含义如下:
              名称	        类型	 描述
              ts_code	    str	    股票代码
              trade_date	str	    交易日期
              open	        float	开盘价
              high	        float	最高价
              low	        float	最低价
              close	        float	收盘价
              pre_close	    float	昨收价【除权价，前复权】
              change	    float	涨跌额
              pct_chg	    float	涨跌幅【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收 】
              vol	        float	成交量（手）
              amount	    float	成交额（千元）
    """

@tushare_mcp.tool()
def daily(
    ts_code:    str = '',
    trade_date: str = '',
    start_date: str = '',
    end_date:   str = '',
    offset:     int = -1,
    limit:      int = -1
) -> str:
    """
    用于查询日维度的交易信息.
    两种用法:
        用法1: 查询指定时间段内,指定股票代码的所有交易日交易信息. 需传入一下三个参数:ts_code, start_date, end_date
        用法2, 查询指定股票代码的所有交易信息, 需传入:ts_code, 其他参数保持默认值
        用法3: 查询某个交易日,所有股票的交易信息. 需传入一下参数: trade_date, 其他参数保持默认值
        用法4: 查询所有股票的所有交易信息, 所有参数保持默认值
    Args:
        ts_code: TS股票代码
        trade_date: 当要查询某个交易日所有股票交易信息时,传入该参数. 格式为: YYYYMMDD. 示例: 20240430
        start_date: 查询开始时间段. 格式为: YYYYMMDD. 示例: 20240430. 传入空串, 则不限制查询时间段.
        end_date: 查询结束时间段. 格式为: YYYYMMDD.  示例: 20240430. 传入空串, 则不限制查询时间段.
        offset: 返回数据的开始行数. 主要用于分批次查询. 传入-1时, 默认查询所有数据.
        limit: 本次返回的数据量. 主要用于分批次查询. 传入-1时, 默认查询所有数据.
    Returns:
        str : 交易信息, 第一行为列名, 之后为数据行, 每列用逗号分隔
              包含如下列, 列类型如下,  含义如下:
              名称	        类型	 描述
              ts_code	    str	    股票代码
              trade_date	str	    交易日期
              open	        float	开盘价
              high	        float	最高价
              low	        float	最低价
              close	        float	收盘价
              pre_close	    float	昨收价【除权价，前复权】
              change	    float	涨跌额
              pct_chg	    float	涨跌幅【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收 】
              vol	        float	成交量（手）
              amount	    float	成交额（千元）
    """
    params = {
    }
    if(ts_code != ""):
        params["ts_code"] = ts_code
    if(trade_date != ""):
        params["trade_date"] = trade_date
    if(start_date != ""):
        params["start_date"] = start_date
    if(end_date != ""):
        params["end_date"] = end_date
    if(offset != -1):
        params['offset'] = offset
    if(limit != -1):
        params['limit'] = limit

    df = ts.pro_api(TUSHARE_API_TOKEN).daily(**params)

    return df.to_csv(index=False, header=True, sep=',')


@tushare_mcp.tool()
def stock_basic(
    ts_code: str = '',
    name: str = '',
    market: str = '',
    list_status: str = '',
    exchange: str = '',
    is_hs: str = '',
    fields: str = ''
) -> str :
    """
    获取基础信息数据，包括股票代码、名称、上市日期、退市日期等
    更详细的接口信息参考:https://tushare.pro/document/2?doc_id=25
    Args:
        ts_code:        要查询的TS股票代码. 传入空串表示查询所有
        name:           要查询股票名称. 传入空串表示查询所有
        market:         要查询哪些市场类别: 主板, 创业板, 科创板, CDR, 北交所. 传入空串表示查询所有.
        list_status:    要查询公司的上市状态. L表示查询上市公司, D表示查询退市公司, P表示查询暂停上市公司. 传入空串表示查询所有.
        exchange:       要查询那个交易所代码的股票. SSE表示查询上交所, SZSE表示查询深交所, BSE表示查询北交所, 传入空串表示查询所有.
        is_hs:          要查询的标的类型. 传入空串表示查询所有, N表示查询非沪股通/深股通的标的, H表示查询沪股通标的, S表示查询深股通标的.
        fields:         要查询哪些信息. 传入空串表示查询所有. 可以传入逗号分隔的字段名来指定要查询哪些信息. 支持如下字段: ts_code表示TS代码, symbol表示股票代码, name表示股票名称, area表示地域, industry表示所属行业, fullname表示股票全称, enname表示英文全称, cnspell表示拼音缩写, market表示市场类型:主板/创业板/科创板/CDR, exchange表示交易所代码, curr_type表示交易货币, list_status表示上市状态:L上市 D退市 P暂停上市, list_date表示上市日期, delist_date表示退市日期, is_hs表示是否沪深港通标的:N否 H沪股通 S深股通, act_name表示实控人名称, act_ent_type表示实控人企业性质
    Returns:
        str: 股票基本信息数据, 第一行为列名, 之后为数据行, 每列用逗号分隔
    """

    default_params = {        
        "ts_code": "",
        "name": "",
        "exchange": "",
        "market": "",
        "is_hs": "",
        "list_status": "",
        "limit": "",
        "offset": "",
        "fields": ["ts_code", "symbol", "name", "area", "industry", "cnspell", "market", "list_date", "act_name", "act_ent_type", "fullname", "enname", "exchange", "curr_type", "list_status", "delist_date", "is_hs"]
    }


    if(os.path.exists(STOCK_BASIC_CACHE_FILE) == False or os.path.getctime(STOCK_BASIC_CACHE_FILE) < (datetime.now().timestamp() - STOCK_BASIC_ACCESS_LIMIT)):

        # if no cache data or cache data is older than 1 day, get full data from Tushare API
        full_data_df = ts.pro_api(TUSHARE_API_TOKEN).stock_basic(**default_params)

        # save full data to csv file
        full_data_df.to_csv(STOCK_BASIC_CACHE_FILE, index=False, header=True, sep=',')
    else:
        # read full data from csv file
        full_data_df = pd.read_csv(STOCK_BASIC_CACHE_FILE, sep=',', header='infer')

    # filter full_data_df based on input parameters
    filtered_data_df = full_data_df.copy()
    if ts_code != '':
        filtered_data_df = filtered_data_df[filtered_data_df['ts_code'] == ts_code ]
    if name != '':
        filtered_data_df = filtered_data_df[filtered_data_df['name'] == name]
    if market != '':
        filtered_data_df = filtered_data_df[filtered_data_df['market'] == market]
    if list_status != '':
        filtered_data_df = filtered_data_df[filtered_data_df['list_status'] == list_status]
    if exchange != '':
        filtered_data_df = filtered_data_df[filtered_data_df['exchange'] == exchange]
    if is_hs != '':
        filtered_data_df = filtered_data_df[filtered_data_df['is_hs'] == is_hs]
    if fields != '':
        filtered_data_df = filtered_data_df[fields.split(",")]
    
    # convert filtered_data_df to csv string
    csv_string = filtered_data_df.to_csv(index=False, header=True, sep=',')
    # return csv string
    return csv_string

def main():

    # read tushare token from parameter --token
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, required=True, help="Tushare token")
    args = parser.parse_args()

    # Initialize Tushare API
    global TUSHARE_API_TOKEN
    TUSHARE_API_TOKEN = args.token

    # define global variable for stock_basic api
    global STOCK_BASIC_CACHE_FILE
    STOCK_BASIC_CACHE_FILE = tempfile.gettempdir() + '/cached_stock_basic.csv'
    global STOCK_BASIC_ACCESS_LIMIT
    STOCK_BASIC_ACCESS_LIMIT = 3600

    # run mcp server
    tushare_mcp.run()

if __name__ == "__main__":
    main()

