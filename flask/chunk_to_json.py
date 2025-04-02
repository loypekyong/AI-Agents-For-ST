import sys
import subprocess
import os
import argparse
from dsrag.knowledge_base import KnowledgeBase

parser = argparse.ArgumentParser(description='Run Jupyter Notebook for chunking.')
parser.add_argument('--kb_id', type=str, default='temp', help='Name of kb (kb_id)')
parser.add_argument('--folder_name', type=str, default='sample', help='Name of folder containing document(s)')

args = parser.parse_args()

# Add the parent directory to the system path
sys.path.append("../")
print(sys.path)

current_path = os.getcwd()
new_folder_path = os.path.join(current_path, args.folder_name)

# Create the new folder if it doesn't exist
if not os.path.exists(new_folder_path):
    os.makedirs(new_folder_path)
    print(f'Created directory: {new_folder_path}')
else:
    print(f'Directory already exists: {new_folder_path}')

# Set variable as os environment to be used by jupyter notebook
os.environ['kb_id'] = args.kb_id

# Run the Jupyter Notebook using nbconvert
notebook_path = 'chunk_to_json.ipynb'  # Replace with the actual path to your notebook
subprocess.run(['jupyter', 'nbconvert', '--to', 'notebook', '--execute', '--inplace', notebook_path])
    

