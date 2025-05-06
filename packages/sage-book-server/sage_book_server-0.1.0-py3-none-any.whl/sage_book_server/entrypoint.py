import subprocess
import os
import sys


def main():
    binary = os.path.join(os.path.dirname(__file__), "bin", "sage-book-server")
    subprocess.run([binary] + sys.argv[1:])
