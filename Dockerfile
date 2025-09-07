FROM python:3.11-slim



RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Create a directory for persistent Python packages

COPY odoo_mcp/requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt --target=/usr/src/app/site-packages

COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

COPY odoo_mcp /usr/src/app/odoo_mcp

ENTRYPOINT ["entrypoint.sh"]
CMD ["python", "-m", "uvicorn", "odoo_mcp.mcp_server:app", "--host", "0.0.0.0"]