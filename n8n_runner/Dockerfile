FROM docker.n8n.io/n8nio/n8n:latest

USER root
WORKDIR /opt/portfolio
COPY workflow.json /opt/portfolio/workflow.json
COPY start.sh /opt/portfolio/start.sh
RUN chmod +x /opt/portfolio/start.sh && chown -R node:node /opt/portfolio
USER node

ENV N8N_RUNNERS_ENABLED=false
ENTRYPOINT ["/bin/sh", "/opt/portfolio/start.sh"]
