FROM python:3.12
ENV TZ=Europe/Moscow
WORKDIR /api
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
