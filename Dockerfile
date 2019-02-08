FROM ubuntu:latest

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y libmysqlclient-dev
RUN apt-get install -y locales
RUN apt-get install -y ffmpeg

RUN pip3 install --upgrade pip


COPY dprojx/requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
# RUN pip3 install gunicorn

WORKDIR /home/web/pam

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8001

CMD ["python3", "manage.py runserver 0.0.0.0:8001"]
