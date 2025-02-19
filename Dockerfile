FROM python:3.11

ARG ENV=production
ENV DJANGO_ENV=${ENV}
ENV DJANGO_SETTINGS_MODULE=app.settings.${ENV}

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1

WORKDIR /code/

COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/

EXPOSE 8000

CMD if [ "$DJANGO_ENV" = "development" ]; then \
        exec python manage.py runserver 0.0.0.0:8000; \
    else \
        exec gunicorn --workers 3 --timeout 120 --bind 0.0.0.0:8000 app.wsgi:application; \
    fi
