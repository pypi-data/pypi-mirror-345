import json
import os


# Load memory from JSON
def load_memory_from_json(file_path):
    try:
        with open(file_path, 'r') as file:
            memory_data = json.load(file)
        return memory_data
    except FileNotFoundError:
        return []


def clear_memory():
    global memory
    memory = []
    try:
        os.remove('.shellix_memory.json')
        print("Memory file removed.")
    except FileNotFoundError:
        print("No memory file found to remove.")


# Initialize memory
memory = load_memory_from_json('.shellix_memory.json')


def save_memory():
    global memory
    with open('.shellix_memory.json', 'w') as file:
        json.dump(memory, file, indent=4)
