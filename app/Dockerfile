FROM python:3.12
ENV TZ="Europe/Moscow"
RUN date
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
