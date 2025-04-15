1. Install python using following commands :-
   sudo apt install python3 python3-pip

2. Install pMars using the commands below :-
   cd {location of corewars project on system}
   python3 install_pmars.py

3. Tarballs should be such that it should contain a Makefile. On running make it should extract a redcode file - chooseyourfighter.red (as in the example). The contents of this file should be different depending on if the env variable is set or not. Name of tarball to be lastnamefirstname.tgz. All tarballs will be provided to entire class for the Third evaluation. Each student will be provided with a unique environment variable which will be the key to encrypt/decrypt their warriors. The script will run make command which will decrypt the first warrior (basic warrior) if the environment variable is not set and the second warrior(advanced warrior) otherwise. You can use the example provided in canvas. All tarballs are to be stored in /project_directory/tarballs folder. The environment variables are to be stored in Env_variables.csv in root directory.

4. First evaluation :- python3 First_evaluation.py
   This grades all students individually. All tarballs are extracted into the submissions folder and individual warriors fight against the basic warriors. 
   Individual scores file with details is created in core/individual_scores folder. A csv which only has the total score is created at the root directory of the project as final_scores.csv.
   Scoring is as follows:-
   Valid Warrior - 20 points
   Beats basic warriors - 10 each 
   Total - 50 for each warrior.

5. Second evaluation :- python3 Second_evaluation.py
   This should make groups of 4 random students, then take two out of those, and make their respective second warriors fight each other. 1 point is awarded to the students' house for each win,
   Separate group scoring records are stored in Battle_Results folder. Final scores for houses are stored in /project_directory/core/Round2_Results.txt.

6. Creating Hash of all existing warriors:- python3 Hash_calculator.py 
   This script is used to create a csv file as calculated_sha256.csv which is used to store the calculated sha256 sum hash value for all "advanced" warriors.

7. Third evaluation:- python3 Third_evaluation.py
   For this evaluation all students will provide a csv with the sha256 of the warriors that they have decrypted. This csv will be compared with the above mentioned "calculated_sha256.csv".
   For each correct entry the house gets 1 point. Enter the csv as Part3_{Houseno}.csv. and this has to be copied to Third_evaluation folder for evaluation.

8. If a student does not provide a valid warrior in the First evaluation they will be given 0 for that warrior. If the "advanced" warrior is invalid or not found then the other houses get 1 point
   for that entry for both rounds 2 and 3. If both the warriors are exactly the same then the individual points will be divided by half so try to change at least something in the second warrior.
  
9. Run these sequentially as the latter scripts depend on the output of the former.

10. Students are not allowed to alter anything in the working environment as well as the directory structure outside of their own folder. If another house is able to find this that house will get all points of the house in question. 

11. Build process of a makefile should not exceed 30 seconds. Otherwise the student gets a 0 in the first evaluation and their warrior will be considered invalid in the latter evaluations.


