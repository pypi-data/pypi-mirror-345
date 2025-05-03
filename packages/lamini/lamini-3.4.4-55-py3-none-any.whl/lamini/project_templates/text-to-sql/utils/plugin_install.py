import shutil
import subprocess
import sys

def install_vscode_extension(ext_id: str):
    """
    Installs a VS Code extension by its full identifier:
      publisher.extensionName
    """
    # 1. Make sure the `code` command is on PATH
    code_cmd = shutil.which("code")
    if code_cmd is None:
        print("❌ Cannot find `code` in your PATH. "
              "You may need to enable the 'Shell Command: Install 'code' command in PATH' setting in VS Code.")
        sys.exit(1)

    # 2. Call `code --install-extension`
    result = subprocess.run(
        [code_cmd, "--install-extension", ext_id],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌ Failed to install:", ext_id)
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        sys.exit(result.returncode)

    print(f"✅ Successfully installed {ext_id}")

if __name__ == "__main__":
    # example: Microsoft’s Python extension
    install_vscode_extension("ms-python.python")