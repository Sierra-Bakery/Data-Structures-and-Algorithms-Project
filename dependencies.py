import subprocess
import sys

def checkDependencies():
    try:
        __import__("matplotlib")
    except ImportError:
        print("matplotlib not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "--break-system-packages", "--quiet"])
            print("matplotlib installed successfully")
        except subprocess.CalledProcessError:
            print("Could not install matplotlib, please run: pip install matplotlib --break-system-packages")

    try:
        __import__("matplotlib.pyplot")
    except ImportError:
        print("matplotlib.pyplot not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "--break-system-packages", "--quiet"])
            print("matplotlib.pyplot installed successfully")
        except subprocess.CalledProcessError:
            print("Could not install matplotlib.pyplot, please run: pip install matplotlib --break-system-packages")

    try:
        __import__("numpy")
    except ImportError:
        print("numpy not found, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "numpy", "--break-system-packages", "--quiet"])
            print("numpy installed successfully")
        except subprocess.CalledProcessError:
            print("Could not install numpy, please run: pip install numpy --break-system-packages")