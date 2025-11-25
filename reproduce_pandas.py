import sys
print(f"Python version: {sys.version}")
try:
    import pandas as pd
    print(f"Pandas version: {pd.__version__}")
    print("Pandas imported successfully.")
except ImportError as e:
    print(f"Error importing pandas: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
