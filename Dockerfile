FROM python:3.9.16-alpine3.17

RUN mkdir /app
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt
CMD ["/bin/sh"]
