#!/bin/bash
echo "📦 Installing YueTransfer Dependencies"
echo "======================================"
echo ""

# Try to find pip in common locations
PIP_CMD=""
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo "❌ Error: pip not found. Please install pip first."
    exit 1
fi

echo "Using pip: $PIP_CMD"
echo "Installing dependencies from requirements.txt..."
echo ""

$PIP_CMD install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Dependencies installed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Configure Google OAuth (optional): python update_google_oauth.py"
    echo "2. Start the server: ./start_server.sh"
    echo ""
else
    echo ""
    echo "❌ Error installing dependencies. Please check your Python/pip installation."
    exit 1
fi