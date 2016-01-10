FROM python:3.5
MAINTAINER Xavier Barbosa <clint.northwood@gmail.com>

ENV DISQUE_PORT 7711
ENV DISQUE_VERSION 1.0-rc1

RUN mkdir -p /usr/local/bin
RUN apt-get -y update \
    && apt-get -y install build-essential curl tar \
    && apt-get -y autoremove \
    && apt-get -y clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN curl -LO https://github.com/antirez/disque/archive/${DISQUE_VERSION}.tar.gz
RUN tar zxvf ${DISQUE_VERSION}.tar.gz
RUN cd disque-${DISQUE_VERSION} \
    && make \
    && mv src/disque /usr/local/bin/ \
    && mv src/disque-server /usr/local/bin/disque-server \
    && mv disque.conf /etc/disque.conf \
    && rm -rf disque-${DISQUE_VERSION}
RUN chmod +x /usr/local/bin/disque
RUN chmod +x /usr/local/bin/disque-server
RUN python -m pip install hiredis pytest pytest-cov pytest-flake8 sphinx twine wheel

EXPOSE $DISQUE_PORT

CMD ["/usr/local/bin/disque-server", "/etc/disque.conf", "--port", "$DISQUE_PORT"]
