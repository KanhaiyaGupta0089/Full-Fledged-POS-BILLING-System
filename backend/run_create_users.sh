#!/bin/bash
# Script to create dummy users
# This can be run on Railway or locally

cd /app/backend || cd backend || pwd
python3 manage.py create_dummy_data

