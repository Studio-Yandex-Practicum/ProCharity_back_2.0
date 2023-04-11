FROM python:3.11

RUN mkdir /app

COPY requirements.txt /app

RUN pip3 install -r /app/requirements.txt --no-cache-dir

WORKDIR /app

# RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
# ENV PATH "${PATH}:/root/.poetry/bin"

# COPY poetry.lock pyproject.toml ./
# RUN poetry config virtualenvs.create false
# RUN poetry install --without dev

COPY . .

CMD ["uvicorn src:app", "-b", "0.0.0.0:8000", "-t", "60"]