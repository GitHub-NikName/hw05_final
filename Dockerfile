FROM python:3.9.16-alpine3.17


RUN mkdir /app
RUN addgroup djos && adduser -G djos -s /bin/sh -D djos
RUN chown -R djos:djos /app
USER djos
WORKDIR /app
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
CMD ["sh"]
