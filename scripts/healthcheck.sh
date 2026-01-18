#!/bin/bash
# Health check for Django application

curl -f http://localhost:8000/health/ || exit 1
