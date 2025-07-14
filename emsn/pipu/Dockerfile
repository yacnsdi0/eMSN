
# PIPU Dockerfile
FROM python:3.12-alpine
RUN apk add --no-cache build-base &&     pip install ryu aiohttp pydantic
WORKDIR /app
COPY .. /app
CMD ["ryu-manager", "emsn.pipu.app"]
