#!/usr/bin/env python3
"""
Startup script for Tracerfy Backend
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🚀 {description}")
    print(f"Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False

def setup_environment():
    """Set up the development environment"""
    print("🔧 Setting up Tracerfy Backend environment...")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("📝 Creating .env file from template...")
        if Path(".env.example").exists():
            run_command("cp .env.example .env", "Copying .env.example to .env")
            print("⚠️  Please edit .env file with your configuration")
        else:
            print("❌ .env.example file not found")
            return False
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    return run_command(
        "pip install -r requirements.txt",
        "Installing dependencies"
    )

def setup_database():
    """Set up database migrations"""
    print("\n🗄️  Setting up database...")
    
    # Check if alembic is configured
    if not Path("alembic.ini").exists():
        print("❌ Alembic configuration not found")
        return False
    
    # Run migrations
    return run_command(
        "alembic upgrade head",
        "Running database migrations"
    )

def start_server():
    """Start the development server"""
    print("\n🌟 Starting Tracerfy Backend server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("📊 Health Check: http://localhost:8000/health")
    print("\n🔄 Server is running. Press Ctrl+C to stop.\n")
    
    try:
        os.system("python -m app.main")
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")

def run_tests():
    """Run test suite"""
    return run_command(
        "pytest -v",
        "Running tests"
    )

def format_code():
    """Format code with black and isort"""
    success = True
    success &= run_command("black app/", "Formatting code with black")
    success &= run_command("isort app/", "Sorting imports with isort")
    return success

def lint_code():
    """Lint code with flake8"""
    return run_command(
        "flake8 app/",
        "Linting code with flake8"
    )

def create_migration(message):
    """Create a new database migration"""
    if not message:
        print("❌ Migration message is required")
        return False
    
    return run_command(
        f'alembic revision --autogenerate -m "{message}"',
        f"Creating migration: {message}"
    )

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Tracerfy Backend CLI")
    parser.add_argument("command", choices=[
        "setup", "install", "migrate", "start", "test", 
        "format", "lint", "migration"
    ], help="Command to run")
    parser.add_argument("--message", help="Migration message")
    
    args = parser.parse_args()
    
    print("🎯 Tracerfy Backend CLI")
    print("=" * 50)
    
    if args.command == "setup":
        if not setup_environment():
            sys.exit(1)
        if not install_dependencies():
            sys.exit(1)
        print("\n✅ Environment setup complete!")
        print("📝 Don't forget to edit your .env file")
        
    elif args.command == "install":
        if not install_dependencies():
            sys.exit(1)
            
    elif args.command == "migrate":
        if not setup_database():
            sys.exit(1)
            
    elif args.command == "start":
        start_server()
        
    elif args.command == "test":
        if not run_tests():
            sys.exit(1)
            
    elif args.command == "format":
        if not format_code():
            sys.exit(1)
            
    elif args.command == "lint":
        if not lint_code():
            sys.exit(1)
            
    elif args.command == "migration":
        if not create_migration(args.message):
            sys.exit(1)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
