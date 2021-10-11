# syntax=docker/dockerfile:experimental
FROM python:3.8-slim

RUN apt-get update &&\
    apt-get install -y git &&\
    mkdir ~/.ssh &&\
    ssh-keyscan -t rsa ssh.github.com > ~/.ssh/known_hosts &&\
    git config --global --add url."git@github.com:".insteadOf "https://github.com/" &&\
    echo "IdentityFile ~/.ssh/github_key" >> /etc/ssh/ssh_config &&\
    mkdir /usr/local/app &&\
    pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org certifi

COPY requirements.txt /tmp/requirements.txt
RUN --mount=type=ssh pip  install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r /tmp/requirements.txt  &&\
 rm -rf /tmp/requirements.txt

WORKDIR /usr/local/app

COPY . .
RUN chmod +x ./cmd/*

EXPOSE 9000
ENTRYPOINT ["./cmd/start.sh"]
