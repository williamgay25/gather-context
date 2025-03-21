# Installation Guide for gather-context

This guide will walk you through installing and setting up the `gather-context` tool so it can be used as a command-line utility.

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

## Installation Steps

### 1. Install Required Package

First, install the required `pyperclip` package:

```bash
pip install pyperclip
```

### 2. Create the Script

Save the code to a file named `gather-context.py` in a directory of your choice.

### 3. Make the Script Executable

```bash
chmod +x /path/to/gather-context.py
```

### 4. Create a Symbolic Link

To run the tool from anywhere, add it to a directory in your PATH. Here are two options:

#### Option A: Link to ~/bin (for personal use)

```bash
# Create ~/bin if it doesn't exist
mkdir -p ~/bin

# Create the symbolic link
ln -s /path/to/gather-context.py ~/bin/gather-context

# Make sure ~/bin is in your PATH (add this to your .bashrc or .zshrc if it's not)
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### Option B: Link to /usr/local/bin (for all users, requires sudo)

```bash
sudo ln -s /path/to/gather-context.py /usr/local/bin/gather-context
```

## Usage

Now you can run the tool from any directory:

```bash
# Basic usage - collect all code files in current directory
gather-context

# Specify a different directory
gather-context -d /path/to/project

# Limit file types
gather-context -e "*.py,*.js"

# Exclude specific patterns
gather-context -x "**/tests/**,**/docs/**"

# Limit the total size collected
gather-context -m 500  # Limits to 500 KB

# Show verbose statistics
gather-context -v

# Save to a file instead of copying to clipboard
gather-context -o context.txt
```

## Troubleshooting

### Clipboard Issues

If you encounter clipboard issues:

- **Linux**: Make sure you have `xclip` or `xsel` installed:
  ```bash
  # For xclip
  sudo apt-get install xclip
  
  # For xsel
  sudo apt-get install xsel
  ```

- **macOS**: The clipboard should work without additional packages.

- **Windows**: Make sure you have pip installed `pywin32`.

### Permission Issues

If you encounter "Permission denied" errors:

```bash
# Make sure the script is executable
chmod +x /path/to/gather-context.py

# If using a symbolic link, make sure the link is correct
ls -la /usr/local/bin/gather-context
```

## Customization

You can modify the script to change:

- Default file extensions
- Default directories to exclude
- Output formatting

Edit the `DEFAULT_EXTENSIONS` and `DEFAULT_EXCLUDES` lists at the top of the script.