#!/bin/bash
set -e
gunicorn accumate_backend.wsgi --log-file -