import os
import sys
import re

print("=== re Module Diagnostic ===")

# Check if re module is really the built-in one
print(f"re module path: {re.__file__ if hasattr(re, '__file__') else 'Built-in'}")

# Check if a local file named re.py exists
current_dir_files = os.listdir()
if 're.py' in current_dir_files:
    print("⚠️ Warning: A file named 're.py' exists in the current directory. This can shadow the built-in re module.")
else:
    print("✅ No local 're.py' file found.")

# Check if there's a __pycache__ folder
if '__pycache__' in current_dir_files:
    print("🧹 Consider deleting __pycache__ if you've renamed 're.py' recently.")

# Try using re normally
try:
    test = re.findall(r'\d+', "There are 24 hours in a day")
    print(f"✅ re.findall test passed: {test}")
except Exception as e:
    print(f"❌ re module failed: {e}")

# Check Python version
print(f"Python version: {sys.version}")

print("\nIf there's no warning and everything passed, your environment is fine.")
