import sys

# Add the project directory to the path
project_home = '/home/MZeeshan/naturalis_pink_salt_co'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Import app object
from naturalis_pink_salt_co import app as application  # 👈 must match folder and __init__.py
