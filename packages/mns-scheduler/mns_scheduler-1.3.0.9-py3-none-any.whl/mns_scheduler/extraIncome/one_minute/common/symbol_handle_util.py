import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
import mns_common.constant.extra_income_db_name as extra_income_db_name
import pandas as pd
from mns_common.db.v2.MongodbUtilV2 import MongodbUtilV2

mongodbUtilV2_27019 = MongodbUtilV2('27019', extra_income_db_name.EXTRA_INCOME)


def symbol_add_prefix(symbol):
    symbol_simple = symbol[0:6]
    suffix = symbol[7:9]
    if suffix in ['SH']:
        return '1.' + symbol_simple
    elif suffix in ['SZ']:
        return '0.' + symbol_simple
    elif suffix in ['BJ']:
        return '0.' + symbol_simple


# col_name 保存数据的结婚
def save_fail_data(now_day, symbol_prefix, col_name):
    fail_dict = {'begin_date': now_day,
                 'end_date': now_day,
                 'symbol': symbol_prefix,
                 'col_name': col_name,
                 'type': 'kzz',
                 'sync_day': now_day,
                 'valid': True,
                 }
    fail_df = pd.DataFrame(fail_dict, index=[1])
    mongodbUtilV2_27019.insert_mongo(fail_df, extra_income_db_name.ONE_MINUTE_SYNC_FAIL)


if __name__ == '__main__':
    symbol_add_prefix('000001.SZ')
