from redis import StrictRedis
from config import REDIS_HOST, REDIS_PASS, REDIS_PORT, APPCHECKER_NAME
import os
import logging
import coloredlogs
import traceback

log = logging.getLogger(__name__)
coloredlogs.install(
    logger=log,
    level="DEBUG",
    fmt="[%(levelname)s] %(message)s"
)

#manage redis
class Manage_Redis:
    def __init__(self):
        self.tid = APPCHECKER_NAME  # loccs_apk
        #connect to redis
        if REDIS_PASS:
            self.redis = StrictRedis(
                REDIS_HOST, REDIS_PORT, 0, REDIS_PASS, decode_responses=True)
        else:
            self.redis = StrictRedis(
                REDIS_HOST, REDIS_PORT, decode_responses=True)
    
    def read_from_conf(self):
        file = os.path.abspath(os.path.dirname(__file__) + '/data/targets.txt')
        with open(file,'r') as f:
            for line in f.readlines():
                line = line.strip()
                self.add_todo(line)
        pass

    def todo_init(self):
        #从target读，增加到todo
        self.read_from_conf()
        log.debug(self.status())
        _todo = self.get_todo()
        _finish = self.get_finish()
        _error = self.get_error() 
        #todo不再删除，通过取差值来获取今天剩余的任务量
        app_ids = _todo - _finish - _error
        return app_ids

    def get_todo(self):
        urls = self.redis.smembers(self.tid + "_todo")
        if urls:
            return urls
        else:
            return(set())

    def get_finish(self):
        urls = self.redis.smembers(self.tid + "_finish")
        if urls:
            return urls
        else:
            return(set())

    def get_error(self):
        urls = self.redis.smembers(self.tid + "_error")
        #if empty
        if urls:
            return urls
        else:
            return(set())

    def get_todo_num(self):
        return self.redis.scard(self.tid + '_todo')

    def get_finish_num(self):
        return self.redis.scard(self.tid + '_finish')

    def get_error_num(self):
        return self.redis.scard(self.tid + '_error')

    #add
    #sadd(key, value)
    def add_todo(self, url):
        ret = self.redis.sadd(self.tid + '_todo', url)
        if ret == 1:
            return 0, 'ADD TODO SUCCESS'
        else:
            return 1, 'URL EXISTS'

    def add_finish(self, url):
        ret = self.redis.sadd(self.tid + '_finish', url)
        if ret == 1:
            return 0, 'ADD FINISH SUCCESS'
        else:
            return 1, 'FINISH EXISTS'

    def add_error(self, url):
        ret = self.redis.sadd(self.tid + '_error', url)
        if ret == 1:
            return 0, 'ADD ERROR SUCCESS'
        else:
            return 1, 'ERROR EXISTS'

    #del
    #srem(key, value)
    def del_todo(self, url):
        ret = self.redis.srem(self.tid + '_todo', url)
        if ret == 1:
            return 0, 'REMOVE TODO SUCCESS'
        else:
            return 1, 'URL NOT EXISTS'

    def del_finish(self, url):
        ret = self.redis.srem(self.tid + '_finish', url)
        if ret == 1:
            return 0, 'REMOVE FINISH SUCCESS'
        else:
            return 1, 'URL NOT EXISTS'

    def del_error(self, url):
        ret = self.redis.srem(self.tid + '_error', url)
        if ret == 1:
            return 0, 'REMOVE ERROR SUCCESS'
        else:
            return 1, 'URL NOT EXISTS'

    def status(self):
        #print process status
        return 1, {
            'task': {
                'todo': self.get_todo_num(),
                'finish': self.get_finish_num(),
                'error':self.get_error_num()
            },
        }