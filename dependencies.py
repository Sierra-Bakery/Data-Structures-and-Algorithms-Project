import subprocess
import sys
import platform

# --break-system-packages is Linux only, not needed on Windows
if platform.system() == "Windows":
    PIP_FLAGS = ["--quiet"]
else:
    PIP_FLAGS = ["--break-system-packages", "--quiet"]

def checkDependencies():
    try:
        __import__("matplotlib")
    except ImportError:
        print("matplotlib not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"] + PIP_FLAGS)
            print("matplotlib installed successfully")
        except subprocess.CalledProcessError:
            print("Could not install matplotlib, please run: pip install matplotlib")

    try:
        __import__("matplotlib.pyplot")
    except ImportError:
        print("matplotlib.pyplot not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib"] + PIP_FLAGS)
            print("matplotlib.pyplot installed successfully")
        except subprocess.CalledProcessError:
            print("Could not install matplotlib.pyplot, please run: pip install matplotlib")

    try:
        __import__("numpy")
    except ImportError:
        print("numpy not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy"] + PIP_FLAGS)
            print("numpy installed successfully")
        except subprocess.CalledProcessError:
            print("Could not install numpy, please run: pip install numpy")