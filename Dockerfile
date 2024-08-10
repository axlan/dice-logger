FROM python:3.12.1-alpine3.19
WORKDIR /app

COPY requirements.txt /app/

RUN pip install --user --no-cache-dir -r requirements.txt

COPY *.py /app/
COPY *.sh /app/

CMD ["./run_servers.sh"]
