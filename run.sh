#!/bin/bash
# Fashion Clothes Shop - Run Script

export PYTHONPATH=$PWD/venv/lib/python3.13/site-packages:$PYTHONPATH

echo " Starting Fashion Clothes Shop Backend..."
echo " API will be available at: http://localhost:5000"
echo " Admin login: admin@fashion.com / admin123"
echo ""

python3 app.py
