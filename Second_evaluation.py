#!/usr/bin/env python3
import os
import subprocess
import random
import math
import shutil
import csv
from functools import reduce

SUBMISSIONS_DIR    = "submissions"
CORE_DIR           = "core"
ROUND2_FILE        = os.path.join(CORE_DIR, "Round2_Results.txt")
BATTLE_RESULTS_DIR = "Battle_Results"
TMP_DIR            = "round2_tmp"
MAPPING_CSV        = "Env_variables.csv"  

student_to_house = {}
with open(MAPPING_CSV) as f:
    for house, tarfile, envvar in csv.reader(f):
        student = tarfile.split('.',1)[0].rsplit('_',1)[0]
        student_to_house[student] = int(house)

def gcd(a,b): return math.gcd(a,b)
def lcm(a,b): return a*b//gcd(a,b)
def lcm_list(nums): return reduce(lcm, nums)

def normalize_tracker_files():
    counts = {}
    for h in range(1,5):
        tf = os.path.join(SUBMISSIONS_DIR, f"House_{h}", "Part_2_tracker.txt")
        if not os.path.exists(tf): continue
        lines = [l.strip() for l in open(tf) if l.strip()]
        if lines:
            counts[h] = len(lines)
    if len(counts) < 4:
        print("Cannot normalize: missing data.")
        return
    L = lcm_list(counts.values())
    for h, c in counts.items():
        tf = os.path.join(SUBMISSIONS_DIR, f"House_{h}", "Part_2_tracker.txt")
        lines = [l.strip() for l in open(tf) if l.strip()]
        factor = L // c
        with open(tf, 'w') as f:
            for l in lines:
                f.write((l + "\n") * factor)

def get_next_student(house):
    tf = os.path.join(SUBMISSIONS_DIR, f"House_{house}", "Part_2_tracker.txt")
    if not os.path.exists(tf):
        return None
    lines = open(tf).readlines()
    if not lines:
        return None
    idx = random.randrange(len(lines))
    student = lines[idx].strip()
    open(tf, 'w').writelines(lines[:idx] + lines[idx+1:])
    return student

def update_house_points(house, pts):
    pts_map = {}
    if os.path.exists(ROUND2_FILE):
        for ln in open(ROUND2_FILE):
            k, v = ln.strip().split('-')
            pts_map[k.strip()] = int(v.strip())
    for h in range(1,5):
        pts_map.setdefault(f"House {h}", 0)
    pts_map[f"House {house}"] += pts
    with open(ROUND2_FILE, 'w') as f:
        for k in sorted(pts_map):
            f.write(f"{k} - {pts_map[k]}\n")

def run_match(w1, w2):
    out = subprocess.run(['pmars','-r','1000', '-f', w1, w2],
                         capture_output=True, text=True).stdout.splitlines()
    return out[-1] if out else ""

def parse_match(line):
    p = line.split()
    if not p or p[0].lower() not in ('result:','results:'):
        return None
    return int(p[1]), int(p[2]), int(p[3])

def form_group_and_battle(group_no):
    if os.path.isdir(TMP_DIR):
        shutil.rmtree(TMP_DIR)
    os.makedirs(TMP_DIR)

    group = []
    for h in range(1,5):
        student = get_next_student(h)
        if not student:
            print(f"House_{h} out of students.")
            return False

        house = student_to_house.get(student)
        if house is None:
            print(f"No mapping for {student}")
            continue

        subf = os.path.join(SUBMISSIONS_DIR, f"House_{house}", student)
        if not os.path.isdir(subf):
            print(f"Missing folder {subf}, skipping {student}.")
            continue

        src = os.path.join(subf, 'chooseyourfighter.red')
        dst = os.path.join(TMP_DIR, f"{student}_{house}.red")
        if not os.path.exists(src):
            print(f"Missing chooseyourfighter.red for {student}, skipping.")
            continue

        shutil.copy(src, dst)
        group.append({'id': f"{student}_{house}", 'house': house, 'path': dst, 'folder': subf})

    if len(group) < 4:
        print("Not enough valid students to form a full group.")
        return False

    scores = {1:0, 2:0, 3:0, 4:0}
    logf = os.path.join(BATTLE_RESULTS_DIR, f"group_{group_no}.txt")
    with open(logf, 'w') as gf:
        gf.write("Group Members:\n")
        for m in group:
            gf.write(m['id'] + "\n")
        gf.write("\nMatches (second warrior only):\n")

    n = len(group)
    for i in range(n):
        for j in range(i+1, n):
            A, B = group[i], group[j]
            wA, wB = A['path'], B['path']
            with open(logf, 'a') as gf:
                invalid_A = os.path.exists(os.path.join(A['folder'], 'Invalid.txt'))
                invalid_B = os.path.exists(os.path.join(B['folder'], 'Invalid.txt'))

                if invalid_A and not invalid_B:
                    gf.write(f"{A['id']} is invalid. Point → {B['id']}\n")
                    update_house_points(B['house'], 1)
                    scores[B['house']] += 1
                    continue
                elif invalid_B and not invalid_A:
                    gf.write(f"{B['id']} is invalid. Point → {A['id']}\n")
                    update_house_points(A['house'], 1)
                    scores[A['house']] += 1
                    continue
                elif invalid_A and invalid_B:
                    gf.write(f"Both {A['id']} and {B['id']} are invalid. No points.\n")
                    continue

                if not os.path.exists(wA) or not os.path.exists(wB):
                    if os.path.exists(wA):
                        gf.write(f"{B['id']} missing, point → {A['id']}\n")
                        update_house_points(A['house'], 1)
                        scores[A['house']] += 1
                    elif os.path.exists(wB):
                        gf.write(f"{A['id']} missing, point → {B['id']}\n")
                        update_house_points(B['house'], 1)
                        scores[B['house']] += 1
                    else:
                        gf.write(f"Both missing for {A['id']} vs {B['id']}\n")
                    continue

                res = run_match(wA, wB)
                gf.write(f"{A['id']} vs {B['id']}: {res}\n")
                pr = parse_match(res)
                if pr:
                    if pr[0] > pr[1]:
                        gf.write(f"{A['id']} wins\n")
                        update_house_points(A['house'], 1)
                        scores[A['house']] += 1
                    elif pr[1] > pr[0]:
                        gf.write(f"{B['id']} wins\n")
                        update_house_points(B['house'], 1)
                        scores[B['house']] += 1
                    else:
                        gf.write("Tie\n")
                else:
                    gf.write("Could not parse\n")

    with open(logf, 'a') as gf:
        gf.write("\nGroup Scores:\n")
        for h in range(1,5):
            gf.write(f"House {h}: {scores[h]}\n")

    shutil.rmtree(TMP_DIR)
    print(f"Group {group_no} complete → {logf}")
    return True

def main():
    os.makedirs(BATTLE_RESULTS_DIR, exist_ok=True)
    normalize_tracker_files()
    grp = 1
    while True:
        if any(
            not os.path.exists(os.path.join(SUBMISSIONS_DIR, f"House_{h}", "Part_2_tracker.txt")) or
            not open(os.path.join(SUBMISSIONS_DIR, f"House_{h}", "Part_2_tracker.txt")).readline().strip()
            for h in range(1,5)
        ):
            print("No more full groups.")
            break

        if not form_group_and_battle(grp):
            break
        grp += 1

if __name__ == "__main__":
    main()
