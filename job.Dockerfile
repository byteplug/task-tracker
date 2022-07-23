FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY requirements.txt ./
COPY clean_tasks.py ./

RUN pip install -r requirements.txt

CMD python clean_tasks.py
