FROM python:3.14-slim-trixie
ARG APP_DIR="/app"

# Update runtime
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
 && apt-get distclean

# Setup gunicorn
RUN pip install --no-cache-dir gunicorn

# Install application
COPY "app/requirements.txt" "${APP_DIR}/requirements.txt"
RUN pip install --no-cache-dir -r "${APP_DIR}/requirements.txt"
COPY "app/*.py" "${APP_DIR}/"
COPY "app/templates/*" "${APP_DIR}/templates/"
COPY "app/static/*" "${APP_DIR}/static/"

# Command settings
WORKDIR "${APP_DIR}"
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:5000 --workers=4 --thread=2 --timeout 300 --capture-output"
CMD ["/usr/local/bin/gunicorn", "app:app"]
