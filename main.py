import multiprocessing as mp
import MRedis
from config import APPCHECKER_PROCESS_NUM
import Mmysql
import AppChecker

if __name__ == "__main__":
    with mp.Manager() as manager:
        redis_manager = MRedis.Manage_Redis()
        mysql_manager = Mmysql.Manage_Mysql()
        mysql_manager.create_table()
        appchecker = AppChecker.AppChecker()
        #app_id
        app_ids = redis_manager.todo_init()

        app_ids = manager.list(app_ids)  # share memory
        l = mp.Lock()
        while True:
            plist = []
            for i in range(APPCHECKER_PROCESS_NUM):
                try:
                    p = mp.Process(target=appchecker.run, args=(app_ids, l, redis_manager, mysql_manager))
                    plist.append(p)
                    p.start()
                except:
                    continue
            for p in plist:
                p.join()