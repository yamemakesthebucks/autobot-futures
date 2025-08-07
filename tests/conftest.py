import logging

# Silence all Prefect logs (including temporary server start/stop)
logging.getLogger("prefect").setLevel(logging.CRITICAL)
# Fully disable the server API logger that causes the I/O-on-closed-file error
logging.getLogger("prefect.server.api.server").disabled = True

import os
import sys

# Prepend project root so 'src/' is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
