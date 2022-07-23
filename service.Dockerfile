FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libffi-dev
RUN pip install -r requirements.txt

RUN pip install gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 questionify:app
