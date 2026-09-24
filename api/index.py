import os
import sys

# Ensure root directory is on Python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import server

# Vercel looks for a class named 'handler' subclassing BaseHTTPRequestHandler
class handler(server.AIIADashboardHandler):
    pass
