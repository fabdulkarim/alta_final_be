FROM python:3.6.8

MAINTAINER Fadhil "Fadhil Abdulkarim, fadhil@alterra.id"

# WORKDIR /app

RUN mkdir -p storage/log 

# COPY requirements.txt .
COPY . .

RUN pip install -r requirements.txt

CMD [ "python3", "app.py" ]