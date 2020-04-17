import requests
import re
import multiprocessing as mp
from html import unescape
from tqdm import tqdm
from redis import StrictRedis
import MRedis
from config import APPCHECKER_NAME, APPCHECKER_PROCESS_NUM, APP_STORE_URL
import logging
import coloredlogs
import traceback
import Mmysql
import AppChecker

log = logging.getLogger(__name__)
coloredlogs.install(
    logger=log,
    level="DEBUG",
    fmt="[%(levelname)s] %(message)s"
)

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36","Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}


class AppChecker:
    def download_app(self,app_id,app_name,app_down_url,redis_manager: MRedis.Manage_Redis):
        print("Downloading file: {}".format(app_name))
        try:
            r = requests.get(app_down_url,stream=True)
            file_size = int(r.headers['content-length'])/1024
            
            with open('./apk/'+app_name,'wb') as f:
                log.info("total size: " + str(round(file_size/1024,2)) + 'M，downloading...')
                for data in tqdm(iterable=r.iter_content(1024),total=file_size,unit='k',desc=app_name):
                    f.write(data)
                log.info(app_name + " downloaded")
            redis_manager.add_finish(app_id)
            # 不再删除todo
            # redis_manager.del_todo(app_id)
        except Exception as e:
            redis_manager.add_error(app_id)
            log.warn("error found")

    def get2down(self,app_id,redis_manager: MRedis.Manage_Redis,mysql_manager: Mmysql.Manage_Mysql):
        app_url = APP_STORE_URL + app_id
        r = requests.get(app_url,headers=headers)
        r.encoding = 'utf-8'
        details = re.findall(r"<a class=\"mkapp-btn mab-download\" title=\"下载到电脑\" href=\"javascript:void\(0\);\" onclick=\"zhytools\.downloadApp(.*);\">",r.text)

        #extract info from js
        tmp1,app_name,tmp2,tmp3,app_type,app_down_url,app_version= (details[0][1:-1].split(","))
        app_down_url = unescape(app_down_url)[2:-2]
        app_name = app_name[2:-1]
        app_version = app_version[2:-1]
        #_app_name是带有版本号的
        _app_name = app_name + '_' + app_version + ".apk"
        last_version = mysql_manager.select_version(app_id)

        log.debug(last_version)
        log.debug(app_version)
        if(last_version != app_version):
            log.info("new version found")
            self.download_app(app_id,_app_name,app_down_url,redis_manager)
            #将apk信息存入数据库
            if mysql_manager.select_app(app_id)==():
                version_history = app_version
                mysql_manager.insert_data(app_name,app_id,app_version,version_history)
            else:
                version_history = mysql_manager.select_vhistory(app_id)
                version_history = version_history + ',' + app_version
                mysql_manager.update_data(app_name,app_id,app_version,version_history)
                redis_manager.add_finish(app_id)
        else:
            log.info("no new version")
            redis_manager.add_finish(app_id)

    def run(self, app_ids, l, redis_manager: MRedis.Manage_Redis, mysql_manager: Mmysql.Manage_Mysql):
        app_id = job_accquire(app_ids, l)
        self.get2down(app_id,redis_manager,mysql_manager)

def job_accquire(app_ids, l):
    try:
        l.acquire()
        log.debug(app_ids)
        app_id = app_ids.pop()
        log.debug(app_id)
        l.release()
        return app_id
    except:
        pass