FROM bogem/ftp:latest

COPY . /fetcher-pipeline
WORKDIR /fetcher-pipeline

RUN apt-get update && apt-get install --no-install-recommends -y apt-utils software-properties-common curl

# Install python, pip and requirements
RUN add-apt-repository ppa:deadsnakes/ppa && apt-get update && \
    apt-get install --no-install-recommends -y python3.8 python3.8-distutils && \
    curl -O https://bootstrap.pypa.io/get-pip.py && python3.8 get-pip.py && \
    rm get-pip.py && pip3.8 install -r requirements.txt

# Install Nodejs
RUN curl -sL https://deb.nodesource.com/setup_12.x -o nodesource_setup.sh && \
    bash nodesource_setup.sh && apt-get install --no-install-recommends -y nodejs && \
    npm install pm2 -g

# Install java
ENV JAVA_HOME /usr/local/jdk-11.0.2
ENV PATH $JAVA_HOME/bin:$PATH

RUN curl -O https://download.java.net/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz && \
    tar zxvf openjdk-11.0.2_linux-x64_bin.tar.gz && mv jdk-11* /usr/local/

ENV SENTRY_DSN ''
ENV PM2_PUBLIC_KEY ''
ENV PM2_SECRET_KEY ''

COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]