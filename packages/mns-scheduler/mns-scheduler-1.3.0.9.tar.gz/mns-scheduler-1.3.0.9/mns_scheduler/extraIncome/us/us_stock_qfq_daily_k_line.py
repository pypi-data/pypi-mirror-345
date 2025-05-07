import os
import sys

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)

from mns_common.db.MongodbUtil import MongodbUtil
from mns_common.db.v2.MongodbUtilV2 import MongodbUtilV2
import mns_common.constant.extra_income_db_name as extra_income_db_name
import mns_common.constant.db_name_constant as db_name_constant
import akshare as ak
from loguru import logger
import mns_scheduler.baidu.baidu_yun_pan_handle_service as baidu_yun_pan_handle_service

mongodb_util_27017 = MongodbUtil('27017')
mongodbUtilV2_27019 = MongodbUtilV2('27019', extra_income_db_name.EXTRA_INCOME)


def us_stock_daily_qfq_sync():
    us_stock_path = '/美股/qfq/'
    em_us_stock_info_df = mongodb_util_27017.find_all_data(db_name_constant.EM_US_STOCK_INFO)
    # 将列 A 转为字符串，并提取前三位
    em_us_stock_info_df["simple_symbol"] = em_us_stock_info_df["simple_symbol"].astype(str).str[:3]
    em_us_stock_info_df = em_us_stock_info_df.sort_values(by=['amount'], ascending=False)
    # 上传列表
    baidu_yun_pan_handle_service.upload_to_baidu('美股列表', us_stock_path, em_us_stock_info_df)
    fail_list = []
    for us_stock_one in em_us_stock_info_df.itertuples():
        symbol = us_stock_one.symbol
        name = us_stock_one.name
        try:
            save_one_symbol(us_stock_one, us_stock_path, symbol)
        except BaseException as e:
            logger.error("同步出现异常:{},{},{}", e, symbol, name)
            fail_list.append(symbol)
    fail_stock_df = em_us_stock_info_df.loc[em_us_stock_info_df['symbol'].isin(fail_list)]

    for us_stock_fail_one in fail_stock_df.itertuples():
        symbol = us_stock_fail_one.symbol
        name = us_stock_fail_one.name
        try:
            save_one_symbol(us_stock_fail_one, us_stock_path, symbol)
        except BaseException as e:
            logger.error("同步出现异常:{},{},{}", e, symbol, name)
            fail_list.append(symbol)


def save_one_symbol(us_stock_one, us_stock_path, symbol):
    simple_symbol = us_stock_one.simple_symbol
    code = simple_symbol + '.' + symbol

    us_stock_k_line_df = us_stock_k_line_api(code, k_line_period='daily', start_date='18000101',
                                             end_date='22220101', fq='qfq')
    us_stock_k_line_df['_id'] = us_stock_k_line_df['date'] + '_' + symbol
    us_stock_k_line_df['symbol'] = symbol

    query = {'symbol': symbol}
    if mongodbUtilV2_27019.remove_data(query, extra_income_db_name.US_STOCK_DAILY_QFQ_K_LINE).acknowledged > 0:
        mongodbUtilV2_27019.insert_mongo(us_stock_k_line_df, extra_income_db_name.US_STOCK_DAILY_QFQ_K_LINE)
        del us_stock_k_line_df['_id']
        del us_stock_k_line_df['symbol']

        # 上传列表
        baidu_yun_pan_handle_service.upload_to_baidu(symbol, us_stock_path, us_stock_k_line_df)


def us_stock_k_line_api(symbol='106.GE', k_line_period='daily', start_date='18000101',
                        end_date='22220101', fq='hfq'):
    stock_us_hist_df = ak.stock_us_hist(symbol=symbol,
                                        period=k_line_period,
                                        start_date=start_date,
                                        end_date=end_date,
                                        adjust=fq)
    stock_us_hist_df = stock_us_hist_df.rename(columns={
        "日期": "date",
        "涨跌额": "change_price",
        "涨跌幅": "chg",
        "开盘": "open",
        "最高": "high",
        "最低": "low",
        "收盘": "close",
        "成交量": "volume",
        "成交额": "amount",
        "振幅": "pct_chg",
        "换手率": "exchange"
    })

    return stock_us_hist_df


if __name__ == '__main__':
    # us_stock_k_line_api()
    us_stock_daily_qfq_sync()
