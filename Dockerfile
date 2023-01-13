FROM python:3.10.9

SHELL ["/bin/bash", "-c"]

WORKDIR /usr/src/app/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir logs/
RUN touch logs/celery.log

# copy entrypoint.sh
COPY ./entrypoint.sh .

RUN chmod 777 /usr/src/app/entrypoint.sh

# copy project
COPY . /usr/src/app/

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
