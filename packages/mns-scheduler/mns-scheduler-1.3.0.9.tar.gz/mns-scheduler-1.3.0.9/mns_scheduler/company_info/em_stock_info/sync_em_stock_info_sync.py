import sys
import os

file_path = os.path.abspath(__file__)
end = file_path.index('mns') + 16
project_path = file_path[0:end]
sys.path.append(project_path)
import datetime
import mns_common.component.proxies.proxy_common_api as proxy_common_api
from mns_common.db.MongodbUtil import MongodbUtil
from loguru import logger
import mns_common.api.em.real_time.east_money_stock_a_v2_api as east_money_stock_a_v2_api
import mns_common.api.em.real_time.east_money_debt_api as east_money_debt_api
import mns_common.api.em.real_time.east_money_etf_api as east_money_etf_api
import mns_common.api.em.real_time.east_money_stock_hk_api as east_money_stock_hk_api
import mns_common.api.em.real_time.east_money_stock_us_api as east_money_stock_us_api
import mns_common.constant.db_name_constant as db_name_constant
import mns_common.component.cookie.cookie_info_service as cookie_info_service

mongodb_util = MongodbUtil('27017')


def sync_all_em_stock_info():
    logger.info("同步东方财富a,etf,kzz,us,hk,信息开始")
    now_date = datetime.datetime.now()
    str_now_date = now_date.strftime('%Y-%m-%d %H:%M:%S')
    proxy_ip = proxy_common_api.get_proxy_ip(str_now_date, 5)
    proxies = {"https": proxy_ip}
    try:
        em_a_stock_info_df = east_money_stock_a_v2_api.get_all_real_time_quotes(proxies)
        em_a_stock_info_df['_id'] = em_a_stock_info_df['symbol']
        mongodb_util.save_mongo(em_a_stock_info_df, db_name_constant.EM_A_STOCK_INFO)
    except BaseException as e:
        logger.error("同步东方财富A股信息异常:{}", e)

    try:
        em_etf_info = east_money_etf_api.get_etf_real_time_quotes(proxies)
        em_etf_info['_id'] = em_etf_info['symbol']
        mongodb_util.save_mongo(em_etf_info, db_name_constant.EM_ETF_INFO)
    except BaseException as e:
        logger.error("同步东方财富ETF信息异常:{}", e)

    try:
        em_kzz_info = east_money_debt_api.get_debt_real_time_quotes(proxies)

        em_kzz_info['_id'] = em_kzz_info['symbol']
        mongodb_util.save_mongo(em_kzz_info, db_name_constant.EM_KZZ_INFO)
    except BaseException as e:
        logger.error("同步东方财富可转债信息异常:{}", e)

    em_cookie = cookie_info_service.get_em_cookie()
    try:
        em_hk_stock_info = east_money_stock_hk_api.get_hk_real_time_quotes(em_cookie, proxies)
        em_hk_stock_info['_id'] = em_hk_stock_info['symbol']
        mongodb_util.save_mongo(em_hk_stock_info, db_name_constant.EM_HK_STOCK_INFO)
    except BaseException as e:
        logger.error("同步东方财富港股信息异常:{}", e)

    try:
        em_us_stock_info = east_money_stock_us_api.get_us_stock_real_time_quotes(em_cookie, proxies)
        em_us_stock_info['_id'] = em_us_stock_info['symbol']
        mongodb_util.save_mongo(em_us_stock_info, db_name_constant.EM_US_STOCK_INFO)
    except BaseException as e:
        logger.error("同步东方财富美股信息异常:{}", e)
    logger.info("同步东方财富a,etf,kzz,us,hk,信息完成")


if __name__ == '__main__':
    sync_all_em_stock_info()
