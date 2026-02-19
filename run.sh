#!/bin/bash
# Quick Start Script for Crypto Trading Bot

echo "=================================="
echo "Crypto Trading Bot - Quick Start"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/bin/pip" ] || [ ! -f "venv/lib/python*/site-packages/pandas" ]; then
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

echo ""
echo "=================================="
echo "Starting Trading Bot in PAPER MODE"
echo "=================================="
echo ""

# Run the bot
python src/main.py
