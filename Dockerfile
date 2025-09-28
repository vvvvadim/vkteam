FROM python:3.12
RUN mkdir -p /app
ENV TZ="Europe/Moscow"
RUN date
COPY /app /app
WORKDIR /app
RUN pip install -r
EXPOSE 8000
CMD ["fastapi", "run"]
