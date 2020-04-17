# LOCCS-AppWatcher

## Project Layout

## Project Working Stream

从targets.txt文件中读取APP ID，存入redis

AppChecker从redis读取任务，检查是否更新，将结果存入mysql

## Usage

使用docker启动一个redis `sudo docker run --rm -d --name redis -v ./data:/data -p 6379:6379 redis --requirepass 'your_password'`

使用docker启动一个mysql  `sudo docker run --rm -d --name mysql -e MYSQL_ROOT_PASSWORD='your_password' -v mysql:/var/lib/mysql -p 3306:3306 mysql:5.5`

## TODO
- [ ] Web UI
- [ ] 数据可视化