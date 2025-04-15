#!/usr/bin/env python3
import os
import hashlib
import csv

SUBMISSIONS_DIR = 'submissions'
MAPPING_CSV = 'Env_variables.csv'
OUTPUT_CSV = 'calculated_sha256.csv'

def calculate_sha256(file_path):
    """Calculate SHA256 hash of a file."""
    try:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash
    except Exception as e:
        print(f"Error calculating hash for {file_path}: {e}")
        return "ERROR"

def main():
    mapping_data = []
    try:
        with open(MAPPING_CSV, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    mapping_data.append([row[0], row[1]])
    except Exception as e:
        print(f"Error reading mapping file: {e}")
        return

    results = []
    for house_num, tarfile in mapping_data:
        student_name = tarfile.split('.', 1)[0]
        student_folder = os.path.join(SUBMISSIONS_DIR, f"House_{house_num}", student_name)
        warrior_path = os.path.join(student_folder, 'chooseyourfighter.red')
        invalid_path = os.path.join(student_folder, 'Invalid.txt')
        
        if os.path.exists(invalid_path):
            results.append([house_num, tarfile, "NOT_A_VALID_WARRIOR"])
            print(f"Invalid warrior for {student_name} (Invalid.txt found)")
        elif os.path.exists(warrior_path):
            sha256_hash = calculate_sha256(warrior_path)
            results.append([house_num, tarfile, sha256_hash])
            print(f"Calculated hash for {student_name}: {sha256_hash[:8]}...")
        else:
            print(f"Warning: Warrior file not found for {student_name} in House {house_num}")
            results.append([house_num, tarfile, "FILE_NOT_FOUND"])

    try:
        with open(OUTPUT_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            for row in results:
                writer.writerow(row)
        print(f"Successfully wrote hashes to {OUTPUT_CSV}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == "__main__":
    main()
