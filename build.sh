#!/usr/bin/env bash
set -o errexit

# Install dependencies (cached by Render)
pip install -r requirements.txt

# Only run migrations if needed
flask db upgrade

# Note: Seed manually via Render shell with: python seed_products.py
# Skipping auto-seed to avoid build issues
