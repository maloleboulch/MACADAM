FROM python:alpine

EXPOSE 5000

WORKDIR app

COPY ./ /app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD sleep 150000
