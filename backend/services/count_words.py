import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.sqlite import  count_cached_words
# Run this once at app start
if __name__ == "__main__":
    print("Cached words:", count_cached_words())



