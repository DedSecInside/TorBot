FROM python:3.6-stretch
LABEL maintainer="v1shwa"

# Install PyQt5
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3-pyqt5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN chmod +x install.sh
RUN bash install.sh

ENTRYPOINT ["./torBot", "--ip", "tor"]