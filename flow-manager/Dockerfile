# Flow Manager Dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install poetry && poetry export -f requirements.txt --without-hashes > req.txt
RUN pip install --prefix=/install -r req.txt
COPY flow_manager flow_manager
RUN python -m compileall flow_manager

FROM gcr.io/distroless/python3
WORKDIR /app
COPY --from=builder /install /usr/local
COPY flow_manager flow_manager
EXPOSE 8443
CMD ["uvicorn", "flow_manager.app:create_app", "--host", "0.0.0.0", "--port", "8443", "--ssl-keyfile", "/certs/fm.key", "--ssl-certfile", "/certs/fm.pem", "--ssl-ca-certs", "/certs/ca.pem", "--ssl-cert-reqs", "2"]
