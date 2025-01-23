#!/bin/bash

# Iniciar Celery worker
celery -A app.tasks.celery worker --loglevel=info &

# Iniciar Celery beat
celery -A app.tasks.celery beat --loglevel=info
