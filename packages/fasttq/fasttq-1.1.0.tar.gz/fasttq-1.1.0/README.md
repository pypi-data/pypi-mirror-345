# fasttq

#### 介绍
FastTQ是一款由 [德波量化](http://www.wtquant.cn) 开源的基于消息队列的多进程分布式任务调度器，原应用于wtquant量化策略高并发回测。

目前该软件暂时仅支持Python语言，消息队列仅支持Redis，最新版本v1.1.0逻辑进行了大幅简化，同时增加zerorpc远程类的支持。

#### 软件架构
FastTQ 非常轻量化，仅包含3个代码文件：
- client.py -- 主要封装用于访问保存任务主题、任务处理器和任务队列的消息队列的客户端 
- broker.py -- 主要封装任务处理器注册和任务注册的装饰器，以及启动任意多个Worker子进程
- worker.py -- 主要封装任务处理子进程


#### 安装教程

安装FastQ有两种方法：
1.  直接从 [github](https://github.com/wakeblade/fasttq) 或者 [gitee](https://gitee.com/wakeblade/fasttq) 下载源代码，然后置入源代码根目录使用
2.  从 [github](https://github.com/wakeblade/fasttq) 或者 [gitee](https://gitee.com/wakeblade/fasttq) 下载源代码后本地安装：python setup.py install
3.  使用pip安装：pip install fasttq

#### 使用说明

1. 例一： 不用注解方式推送任务
```python
from pathlib import Path

from fasttq import RedisClient, Broker

def parse(path:str):
    print(Path(path).parts)

def scan(root:str, pattern:str):
    return Path(root).glob(pattern)

if __name__ == "__main__":
    client = RedisClient()
    broker = Broker(client)
    broker.addHandler(parse)
    broker.pushJobs(scan("C:\\", "*"))
    broker.start()
```

2. 例二： 用注解方式推送任务
```python
from pathlib import Path

from fasttq import RedisClient, Broker

client = RedisClient("scan")
fq = Broker(client)

@fq.register(topic="parse")
def parse(path:str):
    print(Path(path).parts)
    return Path(path).parts

@fq.jobs(topic="parse", root="C:\\", pattern="*")
def scan(root:str, pattern:str):
    return Path(root).glob(pattern)

if __name__ == "__main__":
    fq.start()
```

#### 参与贡献

如果您觉得 [FastTQ](https://gitee.com/wakeblade/fasttq) 对您工作或者学习有价值，欢迎提供赞助。您捐赠的金额将用于团队持续完善FastQ的新功能和性能。 
![赞赏码](https://gitee.com/wakeblade/x2trade/raw/master/zsm.jpg '赞赏码')
![赞赏码](https://github.com/wakeblade/fasttq/assets/47707905/deeb02cf-4d81-43c6-9d11-f2f04538de11 '赞赏码')