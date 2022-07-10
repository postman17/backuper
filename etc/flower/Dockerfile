FROM python:3.8-slim

# Get latest root certificates
#RUN apt add --no-cache ca-certificates && update-ca-certificates

# Install the required packages
RUN pip install --no-cache-dir redis flower celery

# PYTHONUNBUFFERED: Force stdin, stdout and stderr to be totally unbuffered. (equivalent to `python -u`)
# PYTHONHASHSEED: Enable hash randomization (equivalent to `python -R`)
# PYTHONDONTWRITEBYTECODE: Do not write byte files to disk, since we maintain it as readonly. (equivalent to `python -B`)
ENV PYTHONUNBUFFERED=1 PYTHONHASHSEED=random PYTHONDONTWRITEBYTECODE=1

# Run as a non-root user by default, run as user with least privileges.
USER nobody

CMD flower
