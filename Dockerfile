FROM alpine:3
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apk/repositories && apk add --update --no-cache tzdata py3-numpy py3-scipy
ENV TZ Asia/Shanghai

WORKDIR /app

COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . /app/

EXPOSE 8080
CMD ["python3", "main.py"]
