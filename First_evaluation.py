#!/usr/bin/env python3
import os
import tarfile
import subprocess
import shutil
import csv
import time

TARBALLS_DIR = 'tarballs'
SUBMISSIONS_DIR = 'submissions'
BASIC_DIR = 'basic_warriors'
CORE_DIR = 'core'
INDIVIDUAL_SCORE_DIR = os.path.join(CORE_DIR, 'individual_scores')
FINAL_RESULTS_CSV = 'final_results.csv'
MAPPING_CSV = 'Env_variables.csv'  

BASIC_WARRIORS = ['basic1.red', 'basic2.red', 'basic3.red']
TIMEOUT_SECONDS = 30

def extract_tarball(tarball_path, student_folder):
    try:
        mode = 'r:gz' if tarball_path.endswith(('.tar.gz', '.tgz')) else 'r'
        with tarfile.open(tarball_path, mode) as tar:
            tar.extractall(path=student_folder)
        print(f"Extracted {tarball_path} to {student_folder}")
    except Exception as e:
        print(f"Error extracting {tarball_path}: {e}")

def run_make(student_folder, target=None, timeout=TIMEOUT_SECONDS):
    cmd = ['make'] + ([target] if target else [])
    try:
        proc = subprocess.run(cmd, cwd=student_folder,
                              capture_output=True, text=True, timeout=timeout)
        return True, proc.stdout.strip().splitlines()
    except subprocess.TimeoutExpired:
        print(f"Make command timed out after {timeout} seconds in {student_folder}")
        return False, []
    except Exception as e:
        print(f"Error running make in {student_folder}: {e}")
        return True, []

def run_corewar_against_basic(warrior_file, basic_warrior):
    basic_wrior_path = os.path.join(BASIC_DIR, basic_warrior)
    cmd = ['pmars', '-r', '500', '-P', warrior_file, basic_wrior_path]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        lines = proc.stdout.strip().splitlines()
        return lines[-1] if lines else ""
    except Exception as e:
        print(f"Error running pmars against basic warrior: {e}")
        return ""

def parse_result(result_line):
    try:
        parts = result_line.split()
        if parts[0].lower() not in ['results:', 'result:']:
            return None
        return int(parts[1]), int(parts[2]), int(parts[3])
    except Exception:
        return None

def validate_warrior(student_folder, warrior_filename):
    warrior_path = os.path.join(student_folder, warrior_filename)
    try:
        proc = subprocess.run(['pmars', warrior_path], capture_output=True, text=True)
        output = proc.stdout.strip().splitlines()
    except Exception as e:
        print(f"Error running pmars for validation: {e}")
        return False, []
    
    valid = bool(output and "scores" in output[-1].lower())
    return valid, output

def evaluate_warrior(student_folder, warrior_filename, student_name):
    valid, validation_output = validate_warrior(student_folder, warrior_filename)
    details = []
    if validation_output:
        details.append(f"Validation output: {validation_output[-1]}")
    else:
        details.append("No validation output.")
    if not valid:
        details.append(f"Validation failed for {warrior_filename}. Score: 0")
        return 0, "\n".join(details)

    score = 20
    details.append(f"Validation passed for {warrior_filename}: +20 points")
    warrior_path = os.path.join(student_folder, warrior_filename)
    for basic in BASIC_WARRIORS:
        result = run_corewar_against_basic(warrior_path, basic)
        parsed = parse_result(result)
        if parsed and parsed[0] > parsed[1]:
            score += 10
            details.append(f"Battle vs {basic}: {result} -> +10")
        else:
            details.append(f"Battle vs {basic}: {result or 'Invalid'} -> +0")
    return score, "\n".join(details)

def update_individual_score(student_name, score, details=""):
    path = os.path.join(INDIVIDUAL_SCORE_DIR, f"{student_name}_Score.txt")
    try:
        with open(path, 'w') as f:
            f.write(f"{student_name} - Total Score: {score}\n")
            if details:
                f.write("Details:\n")
                f.write(details)
        print(f"Updated individual score for {student_name} to {score}")
    except Exception as e:
        print(f"Error updating score for {student_name}: {e}")

def process_student_submission(tarball, house_num, env_var):
    student_name = tarball.split('.', 1)[0]
    house_folder = os.path.join(SUBMISSIONS_DIR, f"House_{house_num}")
    student_folder = os.path.join(house_folder, f"{student_name}")
    os.makedirs(student_folder, exist_ok=True)

    with open(os.path.join(house_folder, "submissions.txt"), "a") as f:
        f.write(f"{student_name}\n")

    extract_tarball(os.path.join(TARBALLS_DIR, tarball), student_folder)

    warrior1_path = os.path.join(student_folder, 'chooseyourfighter.red')
    warrior1_copy_path = os.path.join(student_folder, 'warrior1.red')
    print(f"Generating warrior1 for {student_name}")
    
    success1, _ = run_make(student_folder)
    if not success1:
        print(f"Make timed out for {student_name}'s warrior1.")
        score1 = 0
        det1 = "Warrior1 build timed out after 30 seconds.\n"
        open(warrior1_path, 'w').close()
    elif not os.path.exists(warrior1_path) or os.path.getsize(warrior1_path) == 0:
        print(f"Warrior1 missing/empty for {student_name}.")
        score1 = 0
        det1 = "Warrior1 was missing or empty after build.\n"
        open(warrior1_path, 'w').close()
    else:
        score1, det1 = evaluate_warrior(student_folder, 'chooseyourfighter.red', student_name)
        shutil.copy(warrior1_path, warrior1_copy_path)
        subprocess.run(['make', 'clean'], cwd=student_folder)

    total = score1
    details = f"Warrior1 Evaluation:\n{det1}\n"

    os.environ[env_var] = '1'
    print(f"Env var {env_var}=1 for {student_name}, generating warrior2")
    success2, _ = run_make(student_folder)
    if not success2:
        print(f"Make timed out for {student_name}'s warrior2.")
        score2 = 0
        details += "Warrior2 build timed out after 30 seconds, skipping evaluation.\n"
        open(warrior1_path, 'w').close()
        invalid2 = os.path.join(student_folder, 'Invalid.txt')
        with open(invalid2, 'w') as f:
            f.write("Warrior2 build timed out. Took more than 30 seconds.\n")
        print(f"Created Invalid.txt for {student_name} due to warrior2 timeout")
    elif not os.path.exists(warrior1_path) or os.path.getsize(warrior1_path) == 0:
        print(f"Warrior2 missing/empty for {student_name}.")
        score2 = 0
        details += "Warrior2 was missing or empty after build.\n"
        invalid2 = os.path.join(student_folder, 'Invalid.txt')
        with open(invalid2, 'w') as f:
            f.write("Warrior2 was missing or empty after build.\n")
        print(f"Created Invalid.txt for {student_name} due to warrior2 missing")
    else:
        score2, det2 = evaluate_warrior(student_folder, 'chooseyourfighter.red', student_name)
        total += score2
        details += f"\nWarrior2 Evaluation:\n{det2}\n"
        if os.path.exists(warrior1_copy_path):
            with open(warrior1_copy_path, 'r') as f1, open(warrior1_path, 'r') as f2:
                if f1.read() == f2.read():
                    total //= 2
                    details += "\nWarrior1 and Warrior2 are identical. Total score halved.\n"
                else:
                    details += "\nWarrior1 and Warrior2 are different. Full score retained.\n"
            os.remove(warrior1_copy_path)

    del os.environ[env_var]

    update_individual_score(student_name, total, details)

    with open(FINAL_RESULTS_CSV, 'a', newline='') as frc:
        writer = csv.writer(frc)
        writer.writerow([house_num, tarball, total])

def main():
    for d in [INDIVIDUAL_SCORE_DIR]:
        os.makedirs(d, exist_ok=True)
    for i in range(1, 5):
        os.makedirs(os.path.join(SUBMISSIONS_DIR, f"House_{i}"), exist_ok=True)

    if not os.path.exists(FINAL_RESULTS_CSV):
        with open(FINAL_RESULTS_CSV, 'w', newline='') as f:
            csv.writer(f).writerow(['House number', 'tarfilename', 'Total Score'])

    mapping = {}
    with open(MAPPING_CSV) as mcf:
        reader = csv.reader(mcf)
        for row in reader:
            if len(row) >= 3:
                mapping[row[1]] = (row[0], row[2])

    for tb in os.listdir(TARBALLS_DIR):
        if tb.endswith(('.tar.gz', '.tgz')):
            print(f"\nProcessing {tb} ...")
            house, envv = mapping.get(tb, (None, None))
            if not house:
                print(f"No mapping entry for {tb}, skipping.")
                continue
            process_student_submission(tb, house, envv)

    for i in range(1, 5):
        hf = os.path.join(SUBMISSIONS_DIR, f"House_{i}")
        sf = os.path.join(hf, "submissions.txt")
        if os.path.exists(sf):
            shutil.copy(sf, os.path.join(hf, "Part_2_tracker.txt"))

if __name__ == "__main__":
    main()

