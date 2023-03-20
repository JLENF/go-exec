FROM mysql:8.0.32

ADD go-exec.sql /docker-entrypoint-initdb.d

EXPOSE 3306
CMD ["mysqld"]