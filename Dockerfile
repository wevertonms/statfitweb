FROM python:3.7-slim-buster
LABEL maintainer="wevertonms@gmail.com"
COPY . ./app
WORKDIR /app
# RUN python -m pip install pipenv && python -m pipenv install && pipenv shell
RUN python -m pip install -r requirements.txt
CMD ["python", "-m", "bokeh", "serve", "."]
