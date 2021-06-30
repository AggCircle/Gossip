# myproject/Dockerfile
# 建立 python3.8 环境
FROM python:3.8

# 镜像作者崔鸿达
MAINTAINER CHD

# 设置 python 环境变量
ENV PYTHONUNBUFFERED 1

# 创建 myproject 文件夹
RUN mkdir -p /home/Gossip

# 将 myproject 文件夹为工作目录
WORKDIR /home/Gossip

# 将当前目录加入到工作目录中（. 表示当前目录）
ADD . /home/Gossip

# 更新pip版本
RUN /usr/local/bin/python -m pip install --upgrade pip

# 利用 pip 安装依赖
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 给start.sh可执行权限
RUN chmod +x ./start.sh

ENTRYPOINT ["sh","/home/Gossip/start.sh"]