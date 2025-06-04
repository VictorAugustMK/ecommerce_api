import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "app")))

from app.utils.db.setup import wait_for_db

if __name__ == "__main__":
    wait_for_db()
