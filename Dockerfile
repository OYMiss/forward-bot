# docker build -t forward-bot:alpha .
FROM ubuntu

RUN apt-get update \
&& apt-get install python3 python3-pip -y \
&& pip3 install cqhttp python-telegram-bot pysocks \
&& apt-get remove python3-pip -y && rm -rf /var/lib/apt/lists/*

COPY src/ /forward-bot/
RUN chmod +x /forward-bot/init.sh

CMD [ "sh", "-c", "./forward-bot/init.sh" ]
