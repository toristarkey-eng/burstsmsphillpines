FROM node:22-bookworm-slim AS node
FROM python:3.12-slim-bookworm
COPY --from=node /usr/local/bin/node /usr/local/bin/node
WORKDIR /app
COPY creative_service/requirements.txt /app/creative_service/requirements.txt
RUN pip install --no-cache-dir -r creative_service/requirements.txt
COPY . /app
RUN useradd --system --uid 10001 --create-home renderer && mkdir -p /data && chown renderer:renderer /data
USER renderer
ENV BURST_PRIVATE_DATA=/data
EXPOSE 8000
CMD ["python", "-m", "creative_service.server"]
