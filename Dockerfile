# FROM ubuntu:latest
FROM ubuntu:xenial

RUN apt-get update --fix-missing
RUN apt-get install -y python3
RUN apt-get install -y python3-pip

RUN apt-get install -y locales
RUN apt-get install -y ffmpeg
RUN apt-get install -y libav-tools
RUN pip3 install --upgrade pip


COPY dprojx/requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt

WORKDIR /home/web/pam

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8001

CMD ["python3", "manage.py runserver 0.0.0.0:8001"]
