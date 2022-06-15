FROM python:3.10-alpine

WORKDIR /code
COPY . .

ARG PIP_INSTALL_ARGS=""
RUN pip install $PIP_INSTALL_ARGS .

ENTRYPOINT [ "splitwise2ynab" ]
CMD ["run"]