import subprocess
import time
import sys
import platform

def run_script(script_path):
    while True:
        try:
            print(f"Starting script: {script_path}")
            
            # Determine the correct Python executable based on the OS
            python_executable = sys.executable if platform.system() != "Windows" else "python"

            # Run the script using subprocess
            process = subprocess.Popen([python_executable, script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = process.communicate()  # Wait for the process to finish

            # Decode the output and error messages
            stdout_decoded = stdout.decode() if stdout else ""
            stderr_decoded = stderr.decode() if stderr else ""

            # Print the output of the script
            if stdout_decoded:
                print(f"Output:\n{stdout_decoded}")

            # If there was an error, print the error message
            if stderr_decoded:
                print(f"Error occurred:\n{stderr_decoded}")

            # Check if the script has crashed or finished successfully
            if process.returncode != 0:
                print(f"Script failed with return code {process.returncode}")
            else:
                print(f"Script completed successfully with return code {process.returncode}")

        except Exception as e:
            print(f"Exception occurred: {e}")
        
        # Wait a moment before restarting the script
        print("Restarting the script in 5 seconds...")
        time.sleep(5)

if __name__ == "__main__":
    script_path = r"backend\traffic\slave.py"  # Replace with the path to the Python file you want to run
    run_script(script_path)
