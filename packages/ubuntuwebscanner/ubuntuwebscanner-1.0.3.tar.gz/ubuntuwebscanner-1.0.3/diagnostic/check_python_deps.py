import importlib
import os

def check_python_packages(requirements_path='requirements.txt'):
    print("\n📦 Python Dependencies Check:")
    if not os.path.exists(requirements_path):
        print("requirements.txt not found.")
        return

    with open(requirements_path) as f:
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue
            pkg = line.split('==')[0].strip()
            try:
                importlib.import_module(pkg.replace('-', '_'))
                print(f"{pkg}: ✓ found")
            except ImportError:
                print(f"{pkg}: ✗ MISSING")

if __name__ == "__main__":
    check_python_packages()
