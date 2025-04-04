import subprocess
import argparse

def main(arg1, arg2):
    kb_id = arg1
    folder_name = arg2

    print(kb_id, folder_name)
    print("Converting to json...")
    subprocess.run(['python', 'flask/chunking_to_json.py', '--kb_id', kb_id, '--folder_name', folder_name])
    print("Converted to json!")

    print("Creating graph...")
    subprocess.run(['python', 'flask/create_graph.py'])
    print("Graph created!")
    
    print("Linking graph...")
    subprocess.run(['python', 'flask/link_graph.py'])
    print("Graph linked!")

if __name__ == "__main__":
    # Set up argument parsing for main.py
    parser = argparse.ArgumentParser(description='Main script to run graph building with arguments.')
    parser.add_argument('--kb_id', type=str, required=True, help='Name of kb (kb_id)')
    parser.add_argument('--folder_name', type=str, required=True, help='Name of folder storing the pdf(s)')

    args = parser.parse_args()
    main(args.kb_id, args.folder_name)