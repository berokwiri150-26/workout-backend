#!/bin/bash

echo "🚀 Setting up Workout Tracker API with Python 3.12..."

# Check Python 3.12
if ! command -v python3.12 &> /dev/null; then
    echo "❌ Python 3.12 not found in PATH"
    echo "Available Python versions:"
    ls -la /usr/bin/python*
    exit 1
fi

echo "✅ Found Python 3.12"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3.12 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Navigate to server directory
cd server

# Initialize database
echo "🗄️  Setting up database..."
flask db init
flask db migrate -m "Initial migration"
flask db upgrade head

# Seed database
echo "🌱 Seeding database..."
python seed.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 To activate the virtual environment:"
echo "  source venv/bin/activate"
echo ""
echo "🚀 To run the server:"
echo "  cd server && python app.py"
echo ""
echo "🌐 Server will run at: http://localhost:5555"
echo ""
echo "📚 API Endpoints:"
echo "  GET    /workouts"
echo "  GET    /workouts/<id>"
echo "  POST   /workouts"
echo "  DELETE /workouts/<id>"
echo "  GET    /exercises"
echo "  GET    /exercises/<id>"
echo "  POST   /exercises"
echo "  DELETE /exercises/<id>"
echo "  POST   /workouts/<workout_id>/exercises/<exercise_id>/workout_exercises"