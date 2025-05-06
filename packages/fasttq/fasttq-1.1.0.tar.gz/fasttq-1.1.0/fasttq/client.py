#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

# @Time    :2023/05/27 12:14:34
# @Author  :wakeblade (2390245#qq.com) 
# @version :8.1

"""
client.py -- 消息队列客户端。
1. 负责与消息队列建立连接，查询任务队列、处理器表、Worker队列，为Broker和Worker赋能
2. 目前暂只支持RedisClient,后续计划支持ZmqClient和WSClient
"""

from typing import Any, List, Union, Callable, TypeVar
from abc import ABC, abstractmethod
from enum import Enum
from collections import namedtuple
from time import time, sleep
import os
import uuid
import json
import importlib
from redis import Redis, ConnectionPool

""" 任务描述：(主题, 数据)"""
Task = namedtuple("Task","topic data".split())

def load_class(moduleName:str, className:str):
    """
    从指定模块装入指定类或方法.
    """
    try:
        module = importlib.import_module(moduleName)
        assert module!=None, f"{moduleName}不存在!" 
        # 重载模块，确保如果策略文件中有任何修改，能够立即生效。
        if "_main__" not in moduleName:importlib.reload(module)
        assert hasattr(module, className), f"{moduleName}模块不存在{className}类!" 
        return getattr(module, className)
    except Exception as e:  # noqa
        print(e)
        return None
    
# 转入指定类
def makeHandler(s:str, topic:str):
    """ 将消息队列中处理器描述转换为可执行函数 """

    if ":" in s:
        return None
    
    m, c = json.loads(s)
    handler = load_class(m, c)
    if topic!=".":
        return handler

    if hasattr(handler, topic):
        return getattr(handler, topic)
    
    return None

class QueueType(Enum):
    """ 消息队列类别： 处理器、工人、任务、结果、报错 """
    HANDLER, WORKER, JOB, RESULT, ERROR = range(5)

class Client(ABC):
    """ 消息队列客户端接口类 """

    @abstractmethod
    def config(self)->List[Any]:
        pass

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def names(self)->List[str]:
        pass

    @abstractmethod
    def register(self, topic:str, handle:Union[TypeVar, Callable]):
        pass

    @abstractmethod
    def unregister(self, topic:str):
        pass

    @abstractmethod
    def pushJob(self, topic:str, job:Any)-> int:
        pass

    @abstractmethod
    def pushJobs(self, topic:str, jobs:List[Any], chunk_size = 10)-> int:
        pass

    @abstractmethod
    def pushError(self, topic:str, job:Any)-> int:
        pass

    @abstractmethod
    def getLen(self, name:str)-> int:
        pass

    @abstractmethod
    def timestamp(self, name:str):
        pass

    @abstractmethod
    def getJob(self)-> Task:
        pass

    @abstractmethod
    def getHandler(self, topic:str)-> Callable:
        pass

DEFAULT_REDIS = dict(
    host = "192.168.0.105",
    port = 6379,
    db = 0,  
    password = None  
)

def getRedis(host:str, port:int, db:int, password:str, retry_timeout:int, retry_times:int)->Callable:
    """ 自动重连redis连接池 """
    pool:ConnectionPool = ConnectionPool(host=host, port=port, db=db, password=password, max_connections=20, decode_responses = True)
    def _redis():
        nonlocal pool, host, port, db, password, retry_timeout, retry_times
        for _ in range(retry_times):
            try:
                r = Redis(connection_pool=pool)
                r.ping()
                return r
            except Exception as e:
                print("错误：", e)
                sleep(retry_timeout)
                pool = ConnectionPool(host=host, port=port, db=db, password=password, max_connections=20)
                continue
        os._exit(-1)
    return _redis

class RedisClient(Client):
    """ Redis消息队列客户端 """

    def __init__(self, app_id:str = None, host:str = None, port:int = None, db:int = None, password:str = None, retry_timeout:int = 5, retry_times:int = 3):
        # 应用标识符
        app_id = app_id or uuid.uuid1().hex 
        # redis主机
        host = host or DEFAULT_REDIS["host"]
        # redis端口
        port = port or DEFAULT_REDIS["port"]
        # redis数据库
        db = db or DEFAULT_REDIS["db"]
        # redis访问密码
        password = password or DEFAULT_REDIS["password"]
        # 重试延迟
        retry_timeout = retry_timeout or 5
        # 重试次数
        retry_times = retry_times or 3

        self._config = [app_id, host, port, db, password, retry_timeout, retry_times] 
        self._connect = getRedis(host, port, db, password, retry_timeout, retry_times)
        self._names = {e:f"{app_id}@{e.name}" for e in QueueType}

    def config(self)->List[Any]:
        """ 返回配置参数列表 """
        return self._config

    def connect(self):
        """ 从连接池获取连接 """
        return self._connect()

    def names(self)->List[str]:
        """ 加了appid的所有消息队列名 """
        return self._names

    def register(self, topic:str, handle:Union[TypeVar, Callable, str]):
        """ 注册处理器 """
        if isinstance(handle, str):
            data = handle 
            topic = "."
        elif isinstance(handle, Callable):
            data = json.dumps((handle.__module__, handle.__name__))
            topic = topic or "*"
        else:
            data = json.dumps((handle.__module__, handle.__name__))
            topic = "."
        name = self._names[QueueType.HANDLER]
        with self.connect() as r:
            r.hset(name, topic, data)

    def unregister(self, topic:str):
        """ 取消注册处理器 """
        name = self._names[QueueType.HANDLER]
        with self.connect() as r:
            r.hdel(name, topic)

    def pushJob(self, topic:str, job:Any):
        """ 单任务装入 """
        name = self._names[QueueType.JOB]
        task = Task(topic, str(job))
        with self.connect() as r:
            r.lpush(name, json.dumps(task))
        return 1

    def pushJobs(self, topic:str, jobs:List[Any], chunk_size = 10)-> int:
        """ 多任务装入 """
        name = self._names[QueueType.JOB]
        _jobs = []
        count = 0
        for job in jobs:
            task = Task(topic, str(job))            
            _jobs.append(json.dumps(task))
            if len(_jobs)>chunk_size:
                with self.connect() as r:
                    r.lpush(name, *_jobs)
                _jobs = []   
                count += chunk_size
        if len(_jobs)>0:
            with self.connect() as r:
                r.lpush(name, *_jobs)
            count += len(_jobs)
        return count

    def pushError(self, topic:str, job:Any)-> int:
        name = self._names[QueueType.ERROR]
        task = Task(topic, str(job))
        with self.connect() as r:
            r.lpush(name, json.dumps(task))
        return 1

    def getLen(self, name:str):
        """ 获取任务队列长度 """
        with self.connect() as r:
            for _ in range(self._config[5]):
                l = r.llen(name) 
                if l>0:
                    return l
                sleep(self._config[6])
        return 0

    def timestamp(self, name:str):
        """ 心跳用时间戳 """
        with self.connect() as r:
            r.hset(name, os.getpid(), int(time()))

    def getJob(self)-> Task:
        """ 获取任务 """
        name = self._names[QueueType.JOB]
        with self.connect() as r:
            topic, data = json.loads(r.rpop(name))
        return Task(topic, data)

    def getHandler(self, topic:str)-> Callable:
        """ 获取处理器 """
        name = self._names[QueueType.HANDLER]
        with self.connect() as r:
            for t in (topic, "*", "."):
                if r.hexists(name, t):
                    s = r.hget(name, t)
                    return makeHandler(s, t)
        return None                