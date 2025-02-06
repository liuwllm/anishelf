FROM python:3.12-slim-bookworm

WORKDIR /back

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn","--config", "./app/config/gunicorn_config.py", "app:create_app()"]


