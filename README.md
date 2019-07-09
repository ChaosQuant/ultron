# 1、部署
## 依赖
分布式计算框架依赖的两个python包:

- 1、vision 
- 2、ultron

## 安装方式

下载依赖对应的源码, 然后使用```python setup.py install```进行安装

所有安装过程都是使用virtualenv进行安装.

# 2、启动
## 1、初始化redis
运行init.py对redis进行初始化

## 2、worker启动
在worker节点上后台运行WorkEngine
```
nohup python q5_cluster_work.py
```

## 3、center启动
在center节点上后台运行CentralEngine
```
nohup python q6_cluster_central.py
```
**ps**, central节点也可以启动worker作为worker节点;

**ps**, worker和central的启动顺序不知道又没有关系, 测试过程中先启动central后启动其他节点上的worker时没有反应, 先启动其他节点的worker后启动central, 没有出现问题.


# 3、运行
## 1、将分布式代码提交到各个worker
从客户端向各worker节点提交代码.
```
python submit.py
```
执行完成之后, 各worker节点会在运行WorkEngine的当前目录下生成相应的文件目录, 文件名为submit的packet名, 二级目录名为提交的代码目录名, 提交的代码在二级目录下.

## 2、客户端运行
在客户端运行client代码.

理论上客户端跟worker和central可以不重合, 也可以是其中的某一个节点, 


# 进程监控
使用celery自带的flower插件

```
celery flower --broker=redis://:@10.15.164:6379/1
```
其中, broker的设置必须与上文初始化分布式框架的init内容一致.

运行成功之后可以看到:
```
[I 190709 20:01:45 command:136] Visit me at http://localhost:5555
[I 190709 20:01:45 command:141] Broker: redis://10.15.5.164:6379/1
[I 190709 20:01:45 command:144] Registered tasks:
    ['celery.accumulate',
     'celery.backend_cleanup',
     'celery.chain',
     'celery.chord',
     'celery.chord_unlock',
     'celery.chunks',
     'celery.group',
     'celery.map',
     'celery.starmap']
[I 190709 20:01:46 mixins:229] Connected to redis://10.15.5.164:6379/1
[W 190709 20:01:46 state:120] Substantial drift from celery@1cb27e8c07d4 may mean clocks are out of sync.  Current drift is
    28800 seconds.  [orig: 2019-07-09 20:01:46.072531 recv: 2019-07-09 12:01:46.066486]

/home/vision/venv/venv3/lib/python3.5/site-packages/celery/app/control.py:54: DuplicateNodenameWarning: Received multiple replies from node names: celery@1cb27e8c07d4, celery@kerry-System-Product-Name.
Please make sure you give each node a unique nodename using
the celery worker `-n` option.
  pluralize(len(dupes), 'name'), ', '.join(sorted(dupes)),
```
过程中如果卡住, 请检查broker的设置是否正确.

正确启动之后, 可以通过```localhost:5555```访问flower UI界面了.



