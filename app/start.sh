#!/bin/bash

python manage.py migrate && hypercorn app.asgi:application -b 0.0.0.0:8000