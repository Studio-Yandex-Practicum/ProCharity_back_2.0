FROM python:3.11

RUN mkdir /app

COPY requirements.txt /app

RUN pip3 install -r /app/requirements.txt --no-cache-dir

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN pip install poetry==1.3.2
RUN poetry config virtualenvs.create false
RUN poetry install --without dev

COPY . .

CMD ["gunicorn", "-b", "0.0.0.0:8000", "-t", "60"]