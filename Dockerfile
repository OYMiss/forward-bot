FROM python:3.7.1-alpine3.8

RUN apk add --no-cache libffi-dev openssl-dev build-base \
&& pip install cffi \
&& pip3 install cqhttp \
&& pip3 install python-telegram-bot --upgrade \
&& pip3 install pysocks

COPY src/ /forward-bot/

CMD [ "sh", "./forward-bot/init.sh" ]
