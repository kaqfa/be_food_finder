import os
import sys


sys.path.insert(0, os.path.dirname(__file__)+"/code")

from food_finder.wsgi import application