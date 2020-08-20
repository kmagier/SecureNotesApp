FROM python:3.7-alpine
WORKDIR /notesapp
COPY application application
COPY notesapp.py config.py requirements.txt KM.crt KM.key ./
ENV FLASK_APP notesapp.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_RUN_PORT 5000
# RUN apk add --no-cache gcc musl-dev linux-headers openssl-dev libffi-dev postgresql-dev
RUN apk add gcc musl-dev linux-headers openssl-dev libffi-dev postgresql-dev
RUN pip install -r requirements.txt
# CMD ["gunicorn", "-b", "0.0.0.0:5000", "notesapp:app"]
CMD ["flask", "run", "--cert=KM.crt", "--key=KM.key"]