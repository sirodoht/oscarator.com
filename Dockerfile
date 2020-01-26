FROM python:3.7.6
ENV PYTHONUNBUFFERED 1
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    swig \
    libssl-dev \
    dpkg-dev \
    netcat \
    && rm -rf /var/lib/apt/lists/*

RUN pip install -U pip
COPY requirements.txt /code/
RUN pip install -Ur /code/requirements.txt

COPY CHECKS /app/
WORKDIR /code
COPY . /code/
RUN /code/manage.py collectstatic --noinput
