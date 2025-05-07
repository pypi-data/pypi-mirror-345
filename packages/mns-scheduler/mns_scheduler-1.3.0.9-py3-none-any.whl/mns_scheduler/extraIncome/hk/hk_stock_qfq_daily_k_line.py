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
import mns_scheduler.hk.hk_company_info_sync_service_api as hk_company_info_sync_service_api

mongodb_util_27017 = MongodbUtil('27017')
mongodbUtilV2_27019 = MongodbUtilV2('27019', extra_income_db_name.EXTRA_INCOME)


def hk_stock_daily_qfq_sync():
    hk_stock_path = '/港股/qfq/'
    hk_stock_exist_df = baidu_yun_pan_handle_service.get_file_folder(hk_stock_path)
    hk_stock_exist_df['symbol'] = hk_stock_exist_df['name'].astype(str).str[:5]

    hk_stock_info_df = mongodb_util_27017.find_all_data(db_name_constant.EM_HK_STOCK_INFO)


    hk_stock_info_df = hk_stock_info_df.sort_values(by=['amount'], ascending=False)
    del hk_stock_info_df['_id']
    # 上传港股列表
    baidu_yun_pan_handle_service.upload_to_baidu('港股列表', hk_stock_path, hk_stock_info_df)
    hk_ggt_component_df = hk_company_info_sync_service_api.get_hk_ggt_component()
    # 上传港股通列表
    hk_stock_info_ggt_df = hk_stock_info_df.loc[hk_stock_info_df['symbol'].isin(hk_ggt_component_df['symbol'])]
    baidu_yun_pan_handle_service.upload_to_baidu('港股通列表', hk_stock_path, hk_stock_info_ggt_df)
    hk_stock_info_df = hk_stock_info_df.loc[~(hk_stock_info_df['symbol'].isin(hk_stock_exist_df['symbol']))]
    fail_list = []

    for hk_stock_one in hk_stock_info_df.itertuples():
        symbol = hk_stock_one.symbol
        name = hk_stock_one.name
        try:
            save_one_symbol(symbol, hk_stock_path)

        except BaseException as e:
            logger.error("同步出现异常:{},{},{}", e, symbol, name)
            fail_list.append(symbol)
    # 处理失败的
    for symbol_fail in fail_list:
        try:
            save_one_symbol(symbol_fail, hk_stock_path)
        except BaseException as e:
            logger.error("同步出现异常:{},{},{}", e, symbol, name)


def save_one_symbol(symbol, hk_stock_path):
    hk_stock_k_line_df = hk_stock_k_line_api(symbol, k_line_period='daily', start_date='18000101',
                                             end_date='22220101', fq='qfq')

    hk_stock_k_line_df["date"] = hk_stock_k_line_df["date"].astype(str)

    hk_stock_k_line_df['_id'] = hk_stock_k_line_df['date'] + '_' + symbol
    hk_stock_k_line_df['symbol'] = symbol

    query = {'symbol': symbol}
    if mongodbUtilV2_27019.remove_data(query, extra_income_db_name.HK_STOCK_DAILY_QFQ_K_LINE).acknowledged > 0:
        mongodbUtilV2_27019.insert_mongo(hk_stock_k_line_df, extra_income_db_name.HK_STOCK_DAILY_QFQ_K_LINE)
        del hk_stock_k_line_df['_id']
        del hk_stock_k_line_df['symbol']
        # 上传列表
        baidu_yun_pan_handle_service.upload_to_baidu(symbol, hk_stock_path, hk_stock_k_line_df)


def hk_stock_k_line_api(symbol='00001', k_line_period='daily', start_date='18000101',
                        end_date='22220101', fq='qfq'):
    stock_hk_hist_df = ak.stock_hk_hist(symbol=symbol,
                                        period=k_line_period,
                                        start_date=start_date,
                                        end_date=end_date,
                                        adjust=fq)
    stock_hk_hist_df = stock_hk_hist_df.rename(columns={
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

    return stock_hk_hist_df


if __name__ == '__main__':
    # us_stock_k_line_api()
    hk_stock_daily_qfq_sync()
