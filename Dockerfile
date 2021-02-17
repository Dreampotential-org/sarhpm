# FROM ubuntu:latest
FROM ubuntu:xenial

RUN apt-get update --fix-missing
RUN apt-get install -y build-essential \
		  checkinstall \
		  libreadline-gplv2-dev \
		  libncursesw5-dev \
		  libssl-dev \
		  libsqlite3-dev \
		  tk-dev \
		  libgdbm-dev \
		  libc6-dev \
		  libbz2-dev \
		  zlib1g-dev \
		  openssl \
		  libffi-dev \
		  python3-dev \
		  python3-setuptools \
		  wget



# Pull down Python 3.7, build, and install
RUN wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tar.xz
RUN tar xvf Python-3.7.0.tar.xz
RUN Python-3.7.0/configure && make altinstall

RUN apt-get install -y locales
RUN apt-get install -y ffmpeg
RUN apt-get install -y libav-tools

RUN pip3.7 install --upgrade pip


COPY dprojx/requirements.txt /tmp/requirements.txt
RUN pip3.7 install -r /tmp/requirements.txt

WORKDIR /home/web/pam

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8001

CMD ["python3", "manage.py runserver 0.0.0.0:8001"]
