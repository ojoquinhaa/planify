FROM python:3
WORKDIR /usr/src/app
COPY setup.py ./
RUN pip install -e .
COPY . .
EXPOSE 8080
CMD [ "gunicorn", "app:app" ]