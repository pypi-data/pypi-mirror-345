import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)

from loguru import logger
import mns_common.utils.data_frame_util as data_frame_util
from mns_common.db.MongodbUtil import MongodbUtil
from mns_common.db.v2.MongodbUtilV2 import MongodbUtilV2
import mns_scheduler.extraIncome.one_minute.common.db_create_index as db_create_index
import mns_common.constant.extra_income_db_name as extra_income_db_name
from datetime import datetime
import mns_common.api.k_line.stock_minute_data_api as stock_minute_data_api
import mns_scheduler.extraIncome.one_minute.common.symbol_handle_util as symbol_handle_util

mongodb_util_27017 = MongodbUtil('27017')
mongodbUtilV2_27019 = MongodbUtilV2('27019', extra_income_db_name.EXTRA_INCOME)

main_index_list = [
    "000001.SH",
    "000016.SH",
    "000010.SH",
    "000009.SH",
    "000015.SH",
    "399001.SZ",
    "399004.SZ",
    "399005.SZ",
    "399006.SZ",
    "000300.SH",
    "000905.SH",
    "000688.SH",
    "000903.SH",
    "000906.SH",
    "000852.SH",
    "000932.SH",
    "000933.SH",
    "980017.SZ",
    "399808.SZ",
    "399997.SZ",
]


def sync_main_index_one_minute(data_tag):
    now_date = datetime.now()
    now_day = now_date.strftime('%Y-%m-%d')
    year = now_date.strftime('%Y')
    col_name = extra_income_db_name.ONE_MINUTE_K_LINE_BFQ_MAIN_INDEX + '_' + str(year)
    # 创建索引
    db_create_index.create_index(mongodbUtilV2_27019, col_name)
    for symbol in main_index_list:
        try:
            symbol_prefix = symbol_handle_util.symbol_add_prefix(symbol)
            one_min_df = stock_minute_data_api.get_minute_data(symbol_prefix, now_day, now_day, '1', '')
            one_min_df['symbol'] = symbol
            one_min_df['_id'] = one_min_df['symbol'] + '_' + one_min_df['time']
            if data_frame_util.is_empty(one_min_df) or one_min_df.shape[0] < 241:
                logger.error("当前沪深指数分钟数据同步异常:{}", symbol)
                continue
            else:
                del one_min_df['ava_price']
                if data_tag:
                    mongodbUtilV2_27019.insert_mongo(one_min_df, col_name)
                else:
                    mongodbUtilV2_27019.save_mongo(one_min_df, col_name)
        except BaseException as e:
            logger.error("沪深指数分钟数据同步异常:{},｛｝", symbol, e)
        logger.info("沪深指数分钟数据同步完成:{}", symbol)


if __name__ == '__main__':
    sync_main_index_one_minute(False)
