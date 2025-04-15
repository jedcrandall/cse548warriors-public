import subprocess

def run_command(command):
    """Executes a shell command and prints the output."""
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {command}: {e}")
        exit(1)

# Update package list
run_command("sudo apt update")

# Install dependencies
run_command("sudo apt install -y build-essential")
run_command("sudo apt install -y pmars")

# Clone pMARS repository
run_command("git clone https://github.com/mbarbon/pMARS.git")

# Navigate to source directory and compile
run_command("cd pMARS/src/ && make")

# Copy binary to /usr/local/bin/
run_command("sudo cp pMARS/src/pmars /usr/local/bin/")

print("pMARS installation completed successfully!")
