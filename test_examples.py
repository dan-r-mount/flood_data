#!/usr/bin/env python3
"""
Test examples for the Flood Risk Checker
Demonstrates functionality with various postcodes
"""

import subprocess
import sys

def run_flood_check(postcode):
    """Run flood check for a given postcode."""
    try:
        result = subprocess.run([
            sys.executable, 'flood_checker.py', '--postcode', postcode
        ], capture_output=True, text=True, timeout=30)
        
        print(f"Testing postcode: {postcode}")
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        print("-" * 80)
        
    except subprocess.TimeoutExpired:
        print(f"Timeout checking {postcode}")
    except Exception as e:
        print(f"Error checking {postcode}: {e}")

def main():
    """Test the flood checker with various postcodes."""
    print("Flood Risk Checker - Test Examples")
    print("=" * 80)
    
    test_postcodes = [
        "E1W 2RG",   # Wapping, London  
        "LS20 8HL",   # Leeds - 
        "SW2 4BN",  # Balham, London
    ]
    
    for postcode in test_postcodes:
        run_flood_check(postcode)

if __name__ == "__main__":
    main() 