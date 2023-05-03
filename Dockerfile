FROM python:3.11

RUN mkdir /app

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY . .

CMD ["uvicorn", "src:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
