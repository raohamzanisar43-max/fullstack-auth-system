#!/usr/bin/env python3
"""
Script to update PostgreSQL password in .env file
"""

import os
import re

def update_password():
    print("=== PostgreSQL Password Update ===")
    print("Please enter your PostgreSQL password for user 'postgres':")
    
    # Get password from user input
    password = input("Password: ").strip()
    
    if not password:
        print("Error: Password cannot be empty")
        return
    
    # Read current .env file
    env_path = ".env"
    try:
        with open(env_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: {env_path} file not found")
        return
    
    # Update the DATABASE_URL
    pattern = r'DATABASE_URL=postgresql://postgres:YOUR_ACTUAL_PASSWORD@localhost:5432/tracify'
    new_url = f'DATABASE_URL=postgresql://postgres:{password}@localhost:5432/tracify'
    
    if pattern in content:
        content = content.replace(pattern, new_url)
        
        # Write back to file
        with open(env_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Password updated successfully in {env_path}")
        print(f"New DATABASE_URL: {new_url}")
        
        # Test connection
        print("\nTesting database connection...")
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(new_url)
            with engine.connect() as connection:
                result = connection.execute(text('SELECT version();'))
                version = result.fetchone()[0]
                print("✅ Database connection successful!")
                print(f"PostgreSQL version: {version[:50]}...")
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
    else:
        print("Error: DATABASE_URL pattern not found in .env file")

if __name__ == "__main__":
    update_password()
