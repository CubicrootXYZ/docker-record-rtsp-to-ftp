FROM python:3-stretch

# set workdir
WORKDIR /usr/src/app

# install dependencies
RUN apt-get update && apt-get -y dist-upgrade && \
	apt-get -y install ffmpeg libav-tools python3-pip git

# cleanup
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/*

RUN git clone https://github.com/CubicrootXYZ/docker-record-rtsp-to-ftp.git /usr/src/app

RUN pip install ftputil

# entry point
CMD python -u script.py 11122

# expose port
EXPOSE 11122