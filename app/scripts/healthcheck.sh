#!/bin/bash
curl --fail --silent http://localhost:8000/api/health || exit 1
