FROM python:3.12.6-alpine
ENTRYPOINT [ "python", "main.py" ]
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src .
