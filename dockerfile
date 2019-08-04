FROM python:3.6
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY pip.conf /root/.pip/pip.conf
COPY requirements.txt /usr/src/app/
COPY requirements /usr/src/app/requirements/
WORKDIR /usr/src/app/requirements/
RUN pip install --no-index --find-links=/usr/src/app/requirements/ -r ../requirements.txt
RUN rm -rf /usr/src/app
COPY . /usr/src/app
WORKDIR /usr/src/app
CMD [ "python", "./manage.py", "runserver", "0:8000"]
