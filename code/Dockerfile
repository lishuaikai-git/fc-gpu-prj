FROM registry.cn-shanghai.aliyuncs.com/serverless_devs/nvidia-ffmpeg:latest
WORKDIR /usr/src/app
RUN apt-get update --fix-missing
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
COPY . .
ENTRYPOINT [ "python3", "-u", "/usr/src/app/app.py" ]
EXPOSE 9000