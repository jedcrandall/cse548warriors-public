#!/usr/bin/env python3
import os
import csv

CALCULATED_CSV = '../calculated_sha256.csv'
RESULTS_FILE = 'Part3_Points.txt'
CORE_DIR = 'core'

def load_calculated_hashes():
    """Load the calculated SHA256 hashes."""
    calculated = {}
    try:
        with open(CALCULATED_CSV, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3:
                    calculated[(row[0], row[1])] = row[2]
        return calculated
    except Exception as e:
        print(f"Error loading calculated hashes: {e}")
        return {}

def load_house_submissions(house_num):
    """Load a house's submitted hashes."""
    file_path = f'Part3_{house_num}.csv'
    submissions = {}
    try:
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3:
                    submissions[(row[0], row[1])] = row[2]
        return submissions
    except Exception as e:
        print(f"Error loading submissions for House {house_num}: {e}")
        return {}

def update_points(house_points):
    """Update the points file with current standings."""
    try:
        with open(RESULTS_FILE, 'w') as f:
            for house_num in sorted(house_points.keys()):
                f.write(f"House {house_num} - {house_points[house_num]}\n")
        print(f"Updated points in {RESULTS_FILE}")
    except Exception as e:
        print(f"Error updating points file: {e}")

def main():
    house_points = {str(i): 0 for i in range(1, 5)}
    
    calculated = load_calculated_hashes()
    if not calculated:
        print("No calculated hashes found. Exiting.")
        return
    
    for house_num in range(1, 5):
        house_submissions = load_house_submissions(house_num)
        if not house_submissions:
            print(f"No submissions found for House {house_num}")
            continue
        
        print(f"\nProcessing House {house_num} submissions:")
        correct_count = 0
        
        for key, submitted_hash in house_submissions.items():
            entry_house = key[0]
            calculated_hash = calculated.get(key)
            
            if calculated_hash in ["FILE_NOT_FOUND", "NOT_A_VALID_WARRIOR", "ERROR"]:
                if entry_house != str(house_num):
                    print(f"+ Point for {key[1]} ({calculated_hash} from House {entry_house})")
                    correct_count += 1
                else:
                    print(f"- No point for own {calculated_hash}: {key[1]}")
            elif calculated_hash:
                if submitted_hash.lower() == calculated_hash.lower():
                    print(f"✓ Correct hash for {key[1]}")
                    correct_count += 1
                else:
                    print(f"✗ Incorrect hash for {key[1]}")
            else:
                print(f"! {key[1]} has unknown status")
        
        house_points[str(house_num)] = correct_count
        print(f"House {house_num} earned {correct_count} points")
    
    update_points(house_points)
    
    print("\nFinal House Points:")
    for house_num, points in sorted(house_points.items()):
        print(f"House {house_num}: {points}")

if __name__ == "__main__":
    main()
