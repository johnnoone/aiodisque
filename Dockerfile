FROM errorist/py:3.5
MAINTAINER Xavier Barbosa <clint.northwood@gmail.com>

ENV DISQUE_PORT 7777
RUN mkdir -p /usr/local/bin
ADD dockerfiles/disque /usr/local/bin/disque
ADD dockerfiles/disque-server /usr/local/bin/disque-server
ADD dockerfiles/disque.conf /etc/disque.conf
RUN chmod +x /usr/local/bin/disque
RUN chmod +x /usr/local/bin/disque-server

RUN apk add --no-cache gcc python3-dev
RUN python -m pip install hiredis

CMD ["/usr/local/bin/disque-server", "/etc/disque.conf", "--port", "$DISQUE_PORT"]
