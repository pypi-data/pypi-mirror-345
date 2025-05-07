import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
import mns_scheduler.extraIncome.one_minute.index.main_index_sync_task as main_index_sync_task
import mns_scheduler.extraIncome.one_minute.etf.etf_one_minute_sync_task as etf_one_minute_sync_task
import mns_scheduler.extraIncome.one_minute.kzz.kzz_one_minute_sync_task as kzz_one_minute_sync_task
import mns_scheduler.extraIncome.one_minute.stock.stock_one_minute_sync_task as stock_one_minute_sync_task
from datetime import datetime
import mns_common.component.trade_date.trade_date_common_service_api as trade_date_common_service_api


def sync_one_minute_data():
    now_date = datetime.now()
    hour = now_date.hour
    now_day = now_date.strftime('%Y-%m-%d')
    if trade_date_common_service_api.is_trade_day(now_day):
        if 15 < hour < 20:
            main_index_sync_task.sync_main_index_one_minute(True)
            etf_one_minute_sync_task.sync_etf_one_minute(True)
            kzz_one_minute_sync_task.sync_kzz_one_minute(True)
            stock_one_minute_sync_task.sync_stock_one_minute(True)
        elif hour < 9 or hour >= 20:
            main_index_sync_task.sync_main_index_one_minute(False)
            etf_one_minute_sync_task.sync_etf_one_minute(False)
            kzz_one_minute_sync_task.sync_kzz_one_minute(False)
            stock_one_minute_sync_task.sync_stock_one_minute(False)


if __name__ == '__main__':
    sync_one_minute_data()
