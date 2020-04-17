import pymysql
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, DB_NAME, CHARSET
import os
import logging
import coloredlogs
import traceback
import datetime

log = logging.getLogger(__name__)
coloredlogs.install(
    logger=log,
    level="DEBUG",
    fmt="[%(levelname)s] %(message)s"
)

today = datetime.date.today()

#manage rmysql
class Manage_Mysql:
    def __init__(self):
        self.db = pymysql.connect(host=MYSQL_HOST,user=MYSQL_USER,passwd=MYSQL_PASS,db=DB_NAME,charset=CHARSET)
        self.cursor = self.db.cursor()

    def create_table(self):
        sql = 'USE loccs'
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
        sql = '''CREATE TABLE IF NOT EXISTS `loccs_apk`(
                    `id` INT UNSIGNED AUTO_INCREMENT,
                    `app_name` VARCHAR(40) NOT NULL,
                    `app_id` VARCHAR(40) NOT NULL,
                    `latest_version` VARCHAR(40) NOT NULL,
                    `version_history` VARCHAR(200) NOT NULL,
                    `last_check_date` VARCHAR(40) NOT NULL,
                    PRIMARY KEY ( `id` )
                    )DEFAULT CHARSET=utf8;
            '''
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()

    def insert_data(self,app_name,app_id,latest_version,version_history):
        sql = "INSERT INTO loccs_apk(`app_name`,`app_id`,`latest_version`,`version_history`,`last_check_date`) VALUES ('{}', '{}','{}', '{}','{}')".format(app_name,app_id,latest_version,version_history,today)
        log.debug(sql)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()

    def update_data(self,app_name,app_id,latest_version,version_history):
        sql = "UPDATE loccs_apk SET latest_version='{}', version_history='{}',last_check_date='{}' where app_id='{}'".format(latest_version,version_history,today,app_id)
        log.debug(sql)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()

    def select_version(self,app_id):
        sql = '''SELECT latest_version from loccs_apk where app_id='{}'
        '''.format(app_id)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            latest_version = results[0][0]
            return latest_version
        except Exception as e:
            print(e)
    
    def select_vhistory(self,app_id):
        sql = "SELECT version_history from loccs_apk where app_id='{}'".format(app_id)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            latest_version = results[0][0]
            return latest_version
        except Exception as e:
            print(e)

    def select_app(self,app_id):
        sql = "SELECT * from loccs_apk where app_id='{}'".format(app_id)
        try:
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            return results
        except Exception as e:
            print(e)                

    
    def update_checked(self):
        sql = ''
        pass