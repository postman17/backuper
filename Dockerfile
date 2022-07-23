FROM python:3.8-slim

# For python print is view on logs
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt update && apt upgrade -y
RUN apt install -y curl unzip redis-server  \
    build-essential python3-dev libpcre3  \
    libpcre3-dev postgresql-client

# Install poetry and pip packages
RUN pip install poetry --no-cache-dir

ARG DEBUG

ENV DEBUG=${DEBUG}

COPY ./pyproject.toml ./poetry.lock /app/

RUN poetry config virtualenvs.create false \
  && poetry install $(test "$DEBUG" = False && echo "--no-dev") --no-interaction --no-ansi

ENV DJANGO_SETTINGS_MODULE project.settings

RUN mkdir -p /app/logs
RUN chown -R www-data /app/logs

#CMD uwsgi --ini /app/etc/uwsgi.ini
CMD ["python", "project/manage.py", "runserver", "0.0.0.0:8000"]

EXPOSE 8000
