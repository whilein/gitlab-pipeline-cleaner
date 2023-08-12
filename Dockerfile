FROM python:alpine
WORKDIR /app
COPY src .
COPY requirements.txt .
RUN pip install -r requirements.txt
ENTRYPOINT [ "python", "main.py" ]