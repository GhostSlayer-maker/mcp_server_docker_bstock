FROM python:3.11-slim



RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create a directory for persistent Python packages

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt --target=/usr/src/app/site-packages

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

COPY . .

ENTRYPOINT ["entrypoint.sh"]
CMD ["python", "mcp_server.py"]