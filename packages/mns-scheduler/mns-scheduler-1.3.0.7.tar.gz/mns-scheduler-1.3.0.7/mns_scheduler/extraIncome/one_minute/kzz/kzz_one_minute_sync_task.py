import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)

import mns_common.component.em.em_stock_info_api as em_stock_info_api
from loguru import logger
import time
import mns_common.utils.data_frame_util as data_frame_util
from mns_common.db.MongodbUtil import MongodbUtil
import mns_scheduler.extraIncome.one_minute.common.symbol_handle_util as symbol_handle_util
from mns_common.db.v2.MongodbUtilV2 import MongodbUtilV2
import mns_scheduler.extraIncome.one_minute.common.db_create_index as db_create_index
import mns_common.constant.extra_income_db_name as extra_income_db_name
import mns_common.api.k_line.stock_minute_data_api as stock_minute_data_api
from datetime import datetime

mongodb_util_27017 = MongodbUtil('27017')
mongodbUtilV2_27019 = MongodbUtilV2('27019', extra_income_db_name.EXTRA_INCOME)


def sync_kzz_one_minute(data_tag):
    debt_real_time_quotes = em_stock_info_api.get_kzz_info()
    debt_real_time_quotes = classify_symbol(debt_real_time_quotes)
    debt_real_time_quotes['symbol'] = debt_real_time_quotes.apply(
        lambda row: row['symbol'] + '.SZ' if row['classification'] in ['S', 'C']
        else row['symbol'] + '.BJ' if row['classification'] in ['X']
        else row['symbol'] + '.SH',
        axis=1
    )
    # 假设数字格式为 YYYYMMDD
    # debt_real_time_quotes['list_date'] = pd.to_datetime(debt_real_time_quotes['list_date'],
    #                                                     format='%Y%m%d').dt.strftime('%Y-%m-%d')

    debt_real_time_quotes = debt_real_time_quotes.loc[debt_real_time_quotes['amount'] != 0]

    now_date = datetime.now()
    now_day = now_date.strftime('%Y-%m-%d')
    year = now_date.strftime('%Y')
    col_name = extra_income_db_name.ONE_MINUTE_K_LINE_BFQ_KZZ + '_' + str(year)
    # 创建索引
    db_create_index.create_index(mongodbUtilV2_27019, col_name)

    for stock_one in debt_real_time_quotes.itertuples():

        symbol = stock_one.symbol
        symbol_prefix = symbol_handle_util.symbol_add_prefix(symbol)
        try:
            one_min_df = stock_minute_data_api.get_minute_data(symbol_prefix, now_day, now_day, '1', '')
            one_min_df['symbol'] = symbol
            one_min_df['_id'] = one_min_df['symbol'] + '_' + one_min_df['time']
            if data_frame_util.is_empty(one_min_df) or one_min_df.shape[0] < 241:
                symbol_handle_util.save_fail_data(now_day, symbol_prefix, col_name)
                logger.error("当前可转债分钟数据同步异常:{}", symbol)
                continue
            else:
                del one_min_df['ava_price']
                if data_tag:
                    mongodbUtilV2_27019.insert_mongo(one_min_df, col_name)
                else:
                    mongodbUtilV2_27019.save_mongo(one_min_df, col_name)
        except BaseException as e:
            time.sleep(2)
            symbol_handle_util.save_fail_data(now_day, symbol_prefix, col_name)
            logger.error("同步可转债分钟数据出现异常:,{},{},{}", e, symbol, now_day)
        logger.info("同步完可转债分钟数据:{},{}", stock_one.symbol, stock_one.name)


def classify_symbol(debt_real_time_quotes_df):
    debt_real_time_quotes_df['classification'] = debt_real_time_quotes_df['market'].apply(
        lambda market: classify_symbol_one(market))
    return debt_real_time_quotes_df


# 单个股票分类
def classify_symbol_one(market):
    if market == 0:
        return 'S'
    else:
        return 'H'


if __name__ == '__main__':
    3()
