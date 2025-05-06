import subprocess
import os
import sys
import dotenv


def main():

    # Load environment variables
    dotenv.load_dotenv()

    binary = os.path.join(os.path.dirname(__file__), "bin", "sage-book-server")
    subprocess.run([binary] + sys.argv[1:])
