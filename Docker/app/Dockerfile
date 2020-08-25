FROM python:3.7-alpine
WORKDIR /notesapp
COPY application application
COPY notesapp.py config.py requirements.txt CERT.crt KEY.key ./
ENV FLASK_APP notesapp.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 5000
RUN apk add --no-cache gcc musl-dev linux-headers openssl-dev libffi-dev postgresql-dev
RUN pip install -r requirements.txt