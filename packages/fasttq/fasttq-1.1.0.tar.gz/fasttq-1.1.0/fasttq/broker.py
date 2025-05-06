#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

# @Time    :2025/05/01 22:14:34
# @Author  :luckrogy (2390245#qq.com) 
# @version :1.1

"""
broker.py -- FastTQ任务调度器。负责任务装载和任务处理器注册，以及启动任意多个Worker子进程
"""

from typing import Any, Union, Iterable, Callable, TypeVar
from time import time, sleep
import os
import signal
from multiprocessing import Pool, cpu_count
import zerorpc

from .client import Client, RedisClient, QueueType
from .worker import Worker

def getWorker(app_id:str, host:str = None, port:int = None, db:int = None, password:str = None, retry_timeout:int = 5, retry_times:int = 3):
    """ Worker工厂方法 """
    client = RedisClient(app_id, host, port, db, password, retry_timeout, retry_times)
    worker = Worker(client)
    worker.work()

class Broker(object):
    """ 任务调度器类 """
    def __init__(self, client:Client, max_workers:int = 0):
        self.client = client
        self.max_workers = max_workers or cpu_count()-2

    def addHandler(self, func:Union[TypeVar, Callable, str], topic:str = None):
        """ 增加处理器 """
        self.client.register(topic, func)
        return self

    def register(self, topic:str = None, url:str = None):
        """ 函数处理器装饰器 """
        def decorator(x:Union[Callable, TypeVar, object]):
            if url:
                self.client.register(topic, url)
                s = zerorpc.Server(x)
                s.bind(url)
                s.run()
            else:
                self.client.register(topic, x)
            return x
        return decorator        

    def funcHandler(self, topic:str = None):
        """ 函数处理器装饰器 """
        def decorator(func:Callable):
            self.client.register(topic, func)
            return func
        return decorator        
        
    def clsHandler(self, topic:str = None):
        """ 类处理器装饰器 """
        def decorator(cls:TypeVar):
            self.client.register(topic, cls)
            return cls
        return decorator        
        
    def rpcHandler(self, topic:str = None, url:str = None):
        """ ZeroRpc处理器装饰器 """
        def decorator(obj:object):
            self.client.register(topic, url)
            s = zerorpc.Server(obj)
            s.bind(url)
            s.run()
        return decorator        

    def pushJobs(self, jobs:Iterable, topic:str = "", chunk_size = 10):
        """ 多任务推送器 """
        self.client.pushJobs(topic, jobs, chunk_size)
        return self

    def pushJob(self, job:Any, topic:str = ""):
        """ 单任务推送器 """
        self.client.pushJobs(topic, job)
        return self

    def jobs(self, topic:str = "", chunk_size:int = 10, *args, **kwargs):
        """ 任务推送器装饰器 """
        def decorator(func:Callable):
            return self.client.pushJobs(topic, func(*args, **kwargs), chunk_size)
        return decorator     

    def start(self):
        """  调度器主进程 """
        pids = dict()
        timestamp = int(time())
        tokills = []

        # pool = ProcessPoolExecutor(max_workers=self.max_workers)
        pool = Pool(processes=self.max_workers)

        client = self.client
        config = client.config()
        names = client.names()
        while True:
            if self.client.getLen(names[QueueType.JOB])<1:
                break

            with client.connect() as r:
                pids = r.hgetall(names[QueueType.WORKER])

                for pid in pids:
                    if int(pids[pid]) + config[5] < timestamp:
                        os.kill(int(pid), signal.SIGTERM)
                        tokills.append(pid) 
            
                if len(tokills)>0:
                    r.hdel(names[QueueType.WORKER], tokills)
            
            reopens = self.max_workers - len(pids) + len(tokills) 
            while self.client.getLen(names[QueueType.JOB]) > self.max_workers and reopens>0:
                print(reopens, "启动worker")
                pool.apply_async(func=getWorker, args=self.client.config())
                reopens -= 1
            sleep(config[5])

        with client.connect() as r:
            print("删除Session")
            r.delete(*names.values())

        pool.terminate()
        pool.join()
        os._exit(0)
