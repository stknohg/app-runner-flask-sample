# Define global arguments
ARG APP_DIR="/app"

#
# Build image
#
FROM python:3.11-slim-bookworm AS build-env
ARG APP_DIR

# Setup gunicorn
RUN pip install --no-cache-dir gunicorn

# Install application
COPY "app/requirements.txt" "${APP_DIR}/requirements.txt"
RUN pip install --no-cache-dir -r "${APP_DIR}/requirements.txt"
COPY "app/*.py" "${APP_DIR}/"
COPY "app/templates/*" "${APP_DIR}/templates/"
COPY "app/static/*" "${APP_DIR}/static/"

#
# Application image
#
FROM gcr.io/distroless/python3-debian12
ARG APP_DIR

# Copy Application
COPY --from=build-env "${APP_DIR}/" "${APP_DIR}/"
COPY --from=build-env /usr/local/lib/python3.11/site-packages /root/.local/lib/python3.11/site-packages
COPY --from=build-env /usr/local/bin/gunicorn /usr/local/bin/gunicorn

# Command settings
WORKDIR "${APP_DIR}"
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:5000 --workers=4 --thread=2 --timeout 300 --capture-output"
CMD ["/usr/local/bin/gunicorn", "app:app"]
