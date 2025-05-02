# Termux API Python Wrapper - Setup Guide

This guide will help you set up and use the Termux API Python wrapper on your Android device.

## Prerequisites

1. **Termux App**: Install the Termux app from [F-Droid](https://f-droid.org/en/packages/com.termux/) or [Google Play Store](https://play.google.com/store/apps/details?id=com.termux).

2. **Termux API App**: Install the Termux API app from [F-Droid](https://f-droid.org/en/packages/com.termux.api/) or [Google Play Store](https://play.google.com/store/apps/details?id=com.termux.api).

## Installation Methods

### Method 1: Install via pip (Recommended)

This is the easiest way to install the package:

```bash
# Update package lists
pkg update

# Install required packages
pkg install termux-api python pip

# Install the termux-api-python package
pip install termux-api-python
```

If you have the wheel file, you can install it directly:

```bash
pip install /path/to/termux_api_python-0.1.0-py3-none-any.whl
```

Or if you have the source distribution:

```bash
pip install /path/to/termux_api_python-0.1.0.tar.gz
```

### Method 2: Install from Source

If you prefer to install from source:

```bash
# Update package lists
pkg update

# Install required packages
pkg install termux-api python pip git

# Clone the repository (if available)
git clone https://github.com/openhands/termux-api-python.git
cd termux-api-python

# Install the package
pip install .
```

### Method 3: Manual Installation

If you prefer not to use pip:

```bash
# Create a directory for the project
mkdir -p ~/termux-api-python

# Navigate to the directory
cd ~/termux-api-python

# Download the zip file
curl -L -o termux_api_wrapper.zip "https://work-1-delauetvgwzladfs.prod-runtime.all-hands.dev:12000/termux_api_wrapper.zip"

# Extract the zip file
unzip termux_api_wrapper.zip

# Make the example scripts executable
chmod +x examples.py notification_example.py
```

## Usage

### After pip installation

After installing with pip, you can use the package in your Python scripts:

```python
from termux_api_python import TermuxAPI

# Create an instance
termux = TermuxAPI()

# Use the API methods
termux.toast("Hello from Python!")
```

### Running the examples

If you've installed via pip:

```bash
# Copy the example files to your working directory
cp /path/to/examples.py /path/to/notification_example.py .

# Run the examples
python examples.py
python notification_example.py
```

If you've installed manually, navigate to the directory where you extracted the files:

```bash
# Run the examples
python examples.py
python notification_example.py
```

## Troubleshooting

### Permission Issues

If you encounter permission issues, make sure:

1. You've granted all necessary permissions to both Termux and Termux API apps in your Android settings
2. For storage-related functions, run `termux-setup-storage` in Termux to set up storage access

### Command Not Found

If you get "command not found" errors for Termux API commands:

1. Make sure the Termux API app is installed
2. Verify that the termux-api package is installed in Termux:
   ```bash
   pkg install termux-api
   ```

### Python Import Errors

If you get import errors when trying to use the wrapper:

1. Make sure the package is installed correctly: `pip list | grep termux-api-python`
2. If using manual installation, make sure you're running the script from the correct directory

## Additional Resources

- [Termux Wiki](https://wiki.termux.com/wiki/Main_Page)
- [Termux API Documentation](https://wiki.termux.com/wiki/Termux:API)
- [Python Documentation](https://docs.python.org/3/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.