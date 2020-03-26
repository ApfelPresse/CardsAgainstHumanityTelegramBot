FROM python:3.6

LABEL maintainer = "Kevin Stiefel"
LABEL email = "kevsti@yahoo.de"

ENV API_TOKEN 1234567

WORKDIR /app

COPY * ./

RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]