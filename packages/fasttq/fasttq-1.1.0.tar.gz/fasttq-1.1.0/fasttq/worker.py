#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-

# @Time    :2025/05/01 22:14:34
# @Author  :luckrogy (2390245#qq.com) 
# @version :1.1

"""
worker.py -- FastTQ任务机器人。
1. 负责不停从任务队列下载任务，并且查询处理器表获得处理器，然后对任务进行处理
2. 维护心跳，定时向消息队列报告自己的状态，如果一旦挂掉调度器将重启新的Worker子进程
"""

from time import sleep
import os
from threading import Thread

from .client import Client, QueueType

class Worker(object):
    """ 工作子进程 """

    def __init__(self, client:Client):
        self.client = client
        self.handlers = {}
        _ht = Thread(target=self.heartbeat, daemon=True)
        _ht.start()

    def heartbeat(self):
        """ 自动维护心跳 """
        client = self.client
        names = client.names()
        config = client.config()
        while True:
            if client.getLen(names[QueueType.JOB])<1:
                break

            client.timestamp(names[QueueType.WORKER])
            sleep(config[5])

        print(os.getpid(), "退出heartbeat")

    def getHandler(self, topic:str):
        """ 获取处理器 """
        if topic not in self.handlers:
            self.handlers[topic] = self.client.getHandler(topic)
        return self.handlers[topic]

    def work(self):
        """ Worker工作进程 """
        client = self.client
        names = client.names()
        while True:
            l = client.getLen(names[QueueType.JOB])
            if l<1:
                break

            task = client.getJob()
            print(l, os.getpid(), task)
            handler = self.getHandler(task.topic)
            try: 
                result = handler(task.data)
                #todo 是否需要推送结果到RESULT队列
            except Exception as e:
                client.pushError(task.topic, task.data)
                        
        print(os.getpid(), "退出worker")