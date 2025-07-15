#!/bin/bash

# AI Financial Advisor - Development Environment Startup Script
# This script starts all required services in separate terminal windows

echo "🚀 Starting AI Financial Advisor Development Environment..."
echo "=================================================="

# Check if we're in the correct directory
if [ ! -f "dash_app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   (The directory containing dash_app.py)"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "⚠️  Warning: Virtual environment not found at backend/venv"
    echo "   Please run: cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    read -p "Continue anyway? (y/N): " continue_anyway
    if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "⚠️  Warning: Node modules not found at frontend/node_modules"
    echo "   Please run: cd frontend && npm install"
    read -p "Continue anyway? (y/N): " continue_anyway
    if [[ ! $continue_anyway =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Function to open new terminal and run command (works on macOS)
open_terminal_tab() {
    local title=$1
    local command=$2
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        osascript -e "tell application \"Terminal\" to do script \"echo '🔥 $title'; $command\""
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux - try different terminal emulators
        if command -v gnome-terminal &> /dev/null; then
            gnome-terminal --tab --title="$title" -- bash -c "echo '🔥 $title'; $command; exec bash"
        elif command -v xterm &> /dev/null; then
            xterm -title "$title" -e "bash -c 'echo \"🔥 $title\"; $command; exec bash'" &
        else
            echo "⚠️  Please manually run: $command"
        fi
    else
        echo "⚠️  Unsupported OS. Please manually run: $command"
    fi
}

echo "📊 Starting Backend API Server..."
open_terminal_tab "Backend API" "cd '$(pwd)/backend' && source venv/bin/activate && echo 'Backend starting on http://localhost:8000' && python run.py"

sleep 2

echo "⚛️  Starting Frontend React App..."
open_terminal_tab "Frontend React" "cd '$(pwd)/frontend' && echo 'Frontend starting on http://localhost:3000' && npm start"

sleep 2

echo "📈 Starting Dash Analytics Dashboard..."
open_terminal_tab "Dash App" "cd '$(pwd)' && source backend/venv/bin/activate && echo 'Dash app starting on http://localhost:8050' && python dash_app.py"

sleep 2

echo "🔄 Starting Streaming Service..."
open_terminal_tab "Streaming Service" "cd '$(pwd)/streaming' && source ../backend/venv/bin/activate && echo 'Streaming service starting...' && python main.py"

echo ""
echo "✅ All services are starting up!"
echo "=================================================="
echo "🌐 Access URLs:"
echo "   Frontend:      http://localhost:3000"
echo "   Backend API:   http://localhost:8000"
echo "   API Docs:      http://localhost:8000/docs"
echo "   Dash App:      http://localhost:8050"
echo ""
echo "📋 Check the individual terminal windows for detailed logs"
echo "🛑 To stop all services: Close the terminal windows or press Ctrl+C in each"
echo ""
echo "�� Happy developing!" 