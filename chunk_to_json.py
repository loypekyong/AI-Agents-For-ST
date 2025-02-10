import sys
import subprocess
import os

# Add the parent directory to the system path
sys.path.append("../")
print(sys.path)

# Run the Jupyter Notebook using nbconvert
notebook_path = 'chunk_to_json.ipynb'  # Replace with the actual path to your notebook
subprocess.run(['jupyter', 'nbconvert', '--to', 'notebook', '--execute', '--inplace', notebook_path])
    

