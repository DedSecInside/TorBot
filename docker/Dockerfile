FROM python:3
LABEL maintainer="dedsec_inside"

# Install PyQt5
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-pyqt5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN python -m poetry install --no-dev

RUN chmod +x install.sh
RUN bash install.sh

ENTRYPOINT ["./torBot", "--ip", "tor"]