#!/usr/bin/env bash
set -o errexit

# Install dependencies (cached by Render)
pip install -r requirements.txt

# Only run migrations if needed
flask db upgrade

# Seed database with products
flask seed
