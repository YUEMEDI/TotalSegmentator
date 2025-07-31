@echo off
echo 🐳 YueTransfer Docker Runner
echo ============================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker first.
    echo    Visit: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    echo    Visit: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist user_files mkdir user_files
if not exist logs mkdir logs

REM Check command line arguments
if "%1"=="" goto start
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="build" goto build
if "%1"=="logs" goto logs
if "%1"=="shell" goto shell
if "%1"=="clean" goto clean
if "%1"=="production" goto production
if "%1"=="help" goto help
goto help

:start
echo 🚀 Starting YueTransfer...
docker-compose up -d
echo.
echo ✅ YueTransfer is running!
echo 🌐 Web Interface: http://localhost:5000
echo.
pause
goto end

:production
echo 🚀 Starting YueTransfer with nginx reverse proxy...
docker-compose --profile production up -d
echo.
echo ✅ YueTransfer is running!
echo 🌐 Web Interface: http://localhost
echo 🔧 Direct Access: http://localhost:5000
echo.
pause
goto end

:stop
echo 🛑 Stopping YueTransfer...
docker-compose down
echo ✅ YueTransfer stopped.
pause
goto end

:restart
echo 🔄 Restarting YueTransfer...
docker-compose down
timeout /t 2 /nobreak >nul
docker-compose up -d
echo ✅ YueTransfer restarted.
pause
goto end

:build
echo 🔨 Building Docker image...
docker-compose build --no-cache
echo ✅ Build completed.
pause
goto end

:logs
echo 📋 Showing logs...
docker-compose logs -f
goto end

:shell
echo 🐚 Opening shell in container...
docker-compose exec yuetransfer /bin/bash
goto end

:clean
echo 🧹 Cleaning up Docker resources...
docker-compose down --rmi all --volumes --remove-orphans
echo ✅ Cleanup completed.
pause
goto end

:help
echo.
echo Usage: %0 [OPTION]
echo.
echo Options:
echo   start       Start YueTransfer (default)
echo   stop        Stop YueTransfer
echo   restart     Restart YueTransfer
echo   build       Build Docker image
echo   logs        Show logs
echo   shell       Open shell in container
echo   clean       Remove containers and images
echo   production  Start with nginx reverse proxy
echo   help        Show this help
echo.
pause
goto end

:end