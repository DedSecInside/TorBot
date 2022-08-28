FROM python:3.9
LABEL maintainer="dedsec_inside"


RUN apt-get update \
    && apt-get install -y virtualenv \
    && apt-get install -y tor \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

# Create virtual env
RUN virtualenv venv --python=python3.9
RUN source venv/bin/activate
RUN pip install -r requirements.txt


RUN chmod +x install.sh
RUN bash install.sh

ENTRYPOINT ["./run.py", "--ip", "tor"]