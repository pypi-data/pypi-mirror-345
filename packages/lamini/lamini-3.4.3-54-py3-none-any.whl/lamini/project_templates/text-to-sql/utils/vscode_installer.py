import os
import platform
import subprocess
import sys
from pathlib import Path
import shutil


def is_command_available(command):
    """Check if a command is available in PATH."""
    return shutil.which(command) is not None


def find_vscode_path():
    """Find VS Code installation path based on OS."""
    system = platform.system()
    
    if system == "Windows":
        # Common installation paths on Windows
        possible_paths = [
            Path(os.environ.get('LOCALAPPDATA', '')) / "Programs" / "Microsoft VS Code" / "bin" / "code.cmd",
            Path(os.environ.get('PROGRAMFILES', '')) / "Microsoft VS Code" / "bin" / "code.cmd",
            Path(os.environ.get('PROGRAMFILES(X86)', '')) / "Microsoft VS Code" / "bin" / "code.cmd",
        ]
    elif system == "Darwin":  # macOS
        possible_paths = [
            Path("/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"),
            Path.home() / "Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
        ]
    else:  # Linux and others
        possible_paths = [
            Path("/usr/bin/code"),
            Path("/usr/local/bin/code"),
            Path("/snap/bin/code")
        ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None


def install_vscode_command_windows(vscode_path):
    """Add VS Code to PATH on Windows."""
    try:
        # Get the directory containing code.cmd
        vscode_bin_dir = str(vscode_path.parent)
        
        # Get current PATH value
        current_path = os.environ.get('PATH', '')
        
        # Check if already in PATH
        if vscode_bin_dir.lower() in current_path.lower():
            print("VS Code is already in your PATH.")
            return True
        
        # Add VS Code to user's PATH using setx
        subprocess.run(['setx', 'PATH', f"{current_path};{vscode_bin_dir}"], check=True)
        
        print("VS Code added to PATH. Please restart your terminal for changes to take effect.")
        return True
    except Exception as e:
        print(f"Error adding VS Code to PATH: {e}")
        return False


def install_vscode_command_macos(vscode_path):
    """Install 'code' command on macOS."""
    try:
        # On macOS, the VS Code app provides a shell script to install the command
        result = subprocess.run([vscode_path], shell=True, check=True)
        print("VS Code 'code' command installed successfully.")
        return True
    except Exception as e:
        print(f"Error installing 'code' command: {e}")
        
        # Provide manual instructions
        print('*'*100)
        print("\nManual installation steps:")
        print("1. Open VS Code")
        print("2. Press Cmd+Shift+P to open the command palette")
        print("3. Type 'shell command' and select 'Shell Command: Install 'code' command in PATH'")
        return False


def install_vscode_command_linux(vscode_path):
    """Install 'code' command on Linux."""
    try:
        # Create a symbolic link to VS Code in /usr/local/bin/
        target_path = Path("/usr/local/bin/code")
        
        if target_path.exists():
            print("The 'code' command is already available but might not be in your PATH.")
        else:
            # Create symlink (requires sudo)
            subprocess.run(['sudo', 'ln', '-s', str(vscode_path), str(target_path)], check=True)
            print("VS Code 'code' command installed successfully.")
        
        return True
    except Exception as e:
        print(f"Error installing 'code' command: {e}")
        
        # Provide manual instructions
        print('*'*100)
        print("\nManual installation steps:")
        print("1. Open VS Code")
        print("2. Press Ctrl+Shift+P to open the command palette")
        print("3. Type 'shell command' and select 'Shell Command: Install 'code' command in PATH'")
        return False


def apply():
    """Main function to install VS Code 'code' command."""
    print("Checking for VS Code installation...")
    
    if is_command_available("code"):
        print("The 'code' command is already available in your PATH.")
        print("If you're still seeing an error, try restarting your terminal or using the full path to VS Code.")
        return
    
    vscode_path = find_vscode_path()
    
    if not vscode_path:
        print('*'*100)
        print("Could not find VS Code installation.")
        print("Please ensure VS Code is installed correctly.")
        print("\nManual steps to install 'code' command:")
        print("1. Open VS Code")
        print("2. Press Ctrl+Shift+P (Cmd+Shift+P on macOS)")
        print("3. Type 'shell command' and select 'Shell Command: Install 'code' command in PATH'")
        return
    
    print(f"Found VS Code at: {vscode_path}")
    
    system = platform.system()
    if system == "Windows":
        install_vscode_command_windows(vscode_path)
    elif system == "Darwin":  # macOS
        install_vscode_command_macos(vscode_path)
    else:  # Linux and others
        install_vscode_command_linux(vscode_path)
    print('*'*100)
    print("\nIf you continue to have issues, you can also open VS Code and:")
    print("1. Press Ctrl+Shift+P (Cmd+Shift+P on macOS)")
    print("2. Type 'shell command' and select 'Shell Command: Install 'code' command in PATH'")

if __name__ == "__main__":
    apply()

