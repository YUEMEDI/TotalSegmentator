#!/bin/bash

echo "🚀 Starting YUEUPLOAD with correct Python environment"
echo "================================================"
echo ""
echo "Using totalsegmentator conda environment (Python 3.10.13)"
echo "for compatibility with YUETransfer and TotalSegmentator"
echo ""

# Try to find the totalsegmentator conda environment
PYTHON_PATH=""

# Check common conda environment locations
if [ -f "$HOME/.conda/envs/totalsegmentator/bin/python" ]; then
    PYTHON_PATH="$HOME/.conda/envs/totalsegmentator/bin/python"
elif [ -f "/opt/conda/envs/totalsegmentator/bin/python" ]; then
    PYTHON_PATH="/opt/conda/envs/totalsegmentator/bin/python"
elif [ -f "/usr/local/conda/envs/totalsegmentator/bin/python" ]; then
    PYTHON_PATH="/usr/local/conda/envs/totalsegmentator/bin/python"
else
    echo "❌ Error: totalsegmentator conda environment not found"
    echo ""
    echo "Please ensure the totalsegmentator conda environment is installed."
    echo "Or activate it manually: conda activate totalsegmentator"
    echo ""
    exit 1
fi

echo "✅ Found Python: $PYTHON_PATH"
echo ""

# Change to the yueupload directory
cd "$(dirname "$0")"

# Run yueupload with the correct Python environment
echo "🎯 Starting YUEUPLOAD..."
echo ""
"$PYTHON_PATH" run.py

echo ""
echo "👋 YUEUPLOAD stopped"