"""
Simple seed script for credit packages
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'tracify_backend', 'backend'))

from decimal import Decimal

# Simple SQL insert statements
packages_data = [
    ("Starter Pack", 1000, Decimal("20.00"), "Perfect for getting started", 0, True),
    ("Professional Pack", 2000, Decimal("40.00"), "Great for regular users", 0, True),
    ("Business Pack", 5000, Decimal("100.00"), "Ideal for growing businesses", 500, True),
    ("Enterprise Pack", 10000, Decimal("200.00"), "Perfect for large teams", 1000, True),
    ("Ultimate Pack", 20000, Decimal("400.00"), "Maximum value for enterprise", 2500, True),
]

print("Credit packages to seed:")
for name, credits, price, desc, bonus, active in packages_data:
    bonus_text = f" + {bonus} bonus" if bonus > 0 else ""
    print(f"  - {name}: {credits} credits{bonus_text} - ${price}")

print("\nTo seed these packages, run this SQL in your database:")
print("DELETE FROM credit_packages;")

for name, credits, price, desc, bonus, active in packages_data:
    print(f"INSERT INTO credit_packages (name, credits, price, description, bonus_credits, is_active) VALUES ('{name}', {credits}, {price}, '{desc}', {bonus}, {true if active else false});")
