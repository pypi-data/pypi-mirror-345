import os
from datetime import*

# Set up paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# DEFAULT_TEMPLATE_FRONT = os.path.join(BASE_DIR, "static","templates", "front_side_circle.png")
DEFAULT_TEMPLATE_BACK = os.path.join(BASE_DIR, "static","templates", "back_side.png")
LOGO_PATH = os.path.join(BASE_DIR, "static","templates", "company_logo.png")
PROFILE_PIC_PATH = os.path.join(BASE_DIR, "static","templates", "Profile_Picture.png")

COMPANY_LOGO_BACK_PATH = os.path.join(BASE_DIR, "static","templates", "back_company_logo.png")

DEFAULT_OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DEFAULT_FONTS_PATH = os.path.join(BASE_DIR, "static","fonts")

DEFAULT_FRONT_TEMPLATES = [
    os.path.join(BASE_DIR, "static","templates", "front_side_circle.png"),
    os.path.join(BASE_DIR, "static","templates", "front_side_rounded.png"),
    os.path.join(BASE_DIR, "static","templates", "front_side_square.png"),
]

# Ensure output directory exists
os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)