#!/bin/bash

echo "========================================"
echo " AI-Powered Attendance System Setup"
echo "========================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Check MongoDB
if ! command -v mongod &> /dev/null; then
    echo "Warning: MongoDB not found. Make sure MongoDB is installed."
fi

echo ""
echo "Setting up Backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

# Initialize database
echo "Initializing database..."
python init_db.py

cd ..

echo ""
echo "Setting up Frontend..."
cd frontend

# Install npm dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

echo ""
echo "========================================"
echo " Setup Complete!"
echo "========================================"
echo ""
echo "To start the application:"
echo "  1. Start MongoDB (if not running)"
echo "  2. Run backend:  cd backend && source venv/bin/activate && python app.py"
echo "  3. Run frontend: cd frontend && npm start"
echo ""
echo "Backend will be available at: http://localhost:5000"
echo "Frontend will be available at: http://localhost:3000"
echo ""
