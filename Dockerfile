FROM python:alpine

EXPOSE 5000

WORKDIR app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
