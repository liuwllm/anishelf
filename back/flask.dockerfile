FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn","--config", "gunicorn_config.py", "app:app"]


