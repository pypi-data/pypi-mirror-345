FROM python:3.13-slim

WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && pip install --upgrade pip \
    && pip install .[cli] --no-cache-dir \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 8080

ENTRYPOINT ["pydbcx-mcp"]
