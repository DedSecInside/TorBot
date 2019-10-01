FROM python:3.6-stretch
LABEL maintainer="v1shwa"

# Install PyQt5
RUN apt-get update \
    && apt-get install -y python3-pyqt5

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

RUN chmod +x install.sh
RUN bash install.sh

ENTRYPOINT ["./torBot", "--ip", "tor"]