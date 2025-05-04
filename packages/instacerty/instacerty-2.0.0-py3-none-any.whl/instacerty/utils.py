import uuid
import os
from datetime import datetime


# Generate 12 Alphanumeric Character
def get_certy_number():
    certificate_number = (str(uuid.uuid4()).replace('-', '')[:12]).upper()
    return certificate_number

# Get the current working directory
def get_save_directory():
    save_directory = os.getcwd()
    return save_directory

def get_current_directory():
    current_directory=os.path.dirname(__file__)
    return current_directory

# Get current date
def get_current_date():
    current_date = (datetime.now().date()).strftime("%d-%m-%Y")
    return current_date

# Get local images Path
def get_local_image_path(image):
    image_path = os.path.join(get_current_directory(), 'static', 'images', f'{image}')
    if os.path.isfile(image_path):
        return image_path
    else:
        print(f"Error: The image '{image}' could not be found at '{image_path}'.")
        return None

