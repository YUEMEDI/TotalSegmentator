#!/bin/bash

echo "🐳 YueTransfer Docker Runner"
echo "============================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p user_files logs

# Function to show usage
show_usage() {
    echo ""
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  start       Start YueTransfer (default)"
    echo "  stop        Stop YueTransfer"
    echo "  restart     Restart YueTransfer"
    echo "  build       Build Docker image"
    echo "  logs        Show logs"
    echo "  shell       Open shell in container"
    echo "  clean       Remove containers and images"
    echo "  production  Start with nginx reverse proxy"
    echo "  help        Show this help"
    echo ""
}

# Function to start services
start_services() {
    echo "🚀 Starting YueTransfer..."
    if [ "$1" = "production" ]; then
        echo "📡 Starting with nginx reverse proxy..."
        docker-compose --profile production up -d
        echo ""
        echo "✅ YueTransfer is running!"
        echo "🌐 Web Interface: http://localhost"
        echo "🔧 Direct Access: http://localhost:5000"
    else
        docker-compose up -d
        echo ""
        echo "✅ YueTransfer is running!"
        echo "🌐 Web Interface: http://localhost:5000"
    fi
}

# Function to stop services
stop_services() {
    echo "🛑 Stopping YueTransfer..."
    docker-compose down
    echo "✅ YueTransfer stopped."
}

# Function to show logs
show_logs() {
    echo "📋 Showing logs..."
    docker-compose logs -f
}

# Function to open shell
open_shell() {
    echo "🐚 Opening shell in container..."
    docker-compose exec yuetransfer /bin/bash
}

# Function to clean up
clean_up() {
    echo "🧹 Cleaning up Docker resources..."
    docker-compose down --rmi all --volumes --remove-orphans
    echo "✅ Cleanup completed."
}

# Function to build image
build_image() {
    echo "🔨 Building Docker image..."
    docker-compose build --no-cache
    echo "✅ Build completed."
}

# Main script logic
case "${1:-start}" in
    start)
        start_services
        ;;
    production)
        start_services production
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services
        ;;
    logs)
        show_logs
        ;;
    shell)
        open_shell
        ;;
    clean)
        clean_up
        ;;
    build)
        build_image
        ;;
    help|--help|-h)
        show_usage
        ;;
    *)
        echo "❌ Unknown option: $1"
        show_usage
        exit 1
        ;;
esac