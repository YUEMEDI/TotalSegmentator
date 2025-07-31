#!/bin/bash
echo "🚀 Starting YueTransfer Server"
echo "================================"
echo ""
echo "This will start the YueTransfer server with Google OAuth support."
echo ""
echo "Web Interface: http://localhost:5000"
echo ""
read -p "Press Enter to continue..."

# Try to find Python in common locations
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python not found. Please install Python 3.8+"
    exit 1
fi

echo "Using Python: $PYTHON_CMD"
echo "Starting server..."

$PYTHON_CMD start_server_step3_google_fixed.py

echo ""
echo "Press Enter to exit..."
read