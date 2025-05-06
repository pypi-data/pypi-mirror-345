import os
import platform
import subprocess
from pathlib import Path
from colorama import Fore, Style, init
import argparse

init()  # Initialize colorama

# Project version
VERSION = "0.1.2"
REQUIRE = "requirements.txt"


def parse_args():
    parser = argparse.ArgumentParser(description="Python Project Initializer")
    parser.add_argument('--no-venv', action='store_true', help='Skip creating virtual environment')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}', help='Show the version of pyinitpro')
    parser.add_argument('--git-remote', metavar='REMOTE_URL', type=str,
                        help='Add a remote repository URL to the Git repo')
    parser.add_argument('--python-version', metavar='PYTHON_VERSION', type=str,
                        help='Specify Python version for virtual environment')
    parser.add_argument('--dependencies', metavar='DEPENDENCIES', type=str,
                        help=f'Comma-separated list of dependencies to add to {REQUIRE}')
    parser.add_argument('--interactive', action='store_true',
                        help='Enable interactive setup for project structure and files')
    return parser.parse_args()


def prompt_folder_creation():
    folders = []
    print("📁 Let's set up your project structure.")
    while True:
        name = input("Enter folder/subfolder name (or just press Enter to finish): ").strip()
        if not name:
            break
        folders.append(name)
    return folders


def create_project_structure(project_path, folders):
    for folder in folders:
        full_path = project_path / folder
        full_path.mkdir(parents=True, exist_ok=True)
        print(Fore.CYAN + f"📁 Created: {full_path}" + Style.RESET_ALL)


def create_files(project_path, dependencies=None):
    (project_path / REQUIRE).touch()

    # Add dependencies to the requirements.txt file if provided
    if dependencies:
        dependencies = [dep.strip() for dep in dependencies.split(',')]
        with open(project_path / REQUIRE, "w") as f:
            for dep in dependencies:
                f.write(f"{dep}\n")
        print(Fore.YELLOW + "📄 Added dependencies to requirements.txt." + Style.RESET_ALL)
    else:
        # Provide a preconfigured template for `requirements.txt`
        with open(project_path / REQUIRE, "w") as f:
            f.write("""# Preconfigured template
# You can add your dependencies here, e.g.:
# flask
# django
""")
        print(Fore.YELLOW + "📄 Created a preconfigured requirements.txt template." + Style.RESET_ALL)

    with open(project_path / ".gitignore", "w") as f:
        f.write("""# Python
__pycache__/
*.py[cod]
.venv/
.env
""")

    with open(project_path / "main.py", "w") as f:
        f.write("""def main():
    print('Hello, world!')

if __name__ == '__main__':
    main()
""")
    print(Fore.GREEN + "✅ Basic files created." + Style.RESET_ALL)


def create_venv(project_path, python_version=None):
    venv_path = project_path / ".venv"
    python_cmd = f"python{python_version}" if python_version else "python3"

    # Check if the Python version exists on the system
    result = subprocess.run([python_cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(Fore.RED + f"❌ Python version {python_version} is not available on your system." + Style.RESET_ALL)
        return None
    subprocess.run([python_cmd, "-m", "venv", str(venv_path)])
    return venv_path


def activate_virtual_env(venv_path: Path):
    system = platform.system()
    print("\n⚡ Virtual environment created.")
    if system == "Windows":
        activate_script = venv_path / "Scripts" / "activate.bat"
        os.system(f'start cmd /K "{activate_script}"')
    elif system == "Darwin":
        activate_script = venv_path / "bin" / "activate"
        print(f"\n📝 To activate the virtual environment on macOS, run:\n\n    source {activate_script}\n")
    elif system == "Linux":
        activate_script = venv_path / "bin" / "activate"
        if os.system("which gnome-terminal > /dev/null 2>&1") == 0:
            os.system(f'gnome-terminal -- bash -c "source {activate_script}; exec bash"')
        else:
            print(f"\n📝 To activate the virtual environment, run:\n\n    source {activate_script}\n")
    else:
        print("❗ Unsupported OS for auto-activation. Please activate manually.")


def init_git(project_path, remote_url=None):
    try:
        subprocess.run(["git", "init"], cwd=project_path)
        print(Fore.YELLOW + "📘 Git repository initialized." + Style.RESET_ALL)
        if remote_url:
            subprocess.run(["git", "remote", "add", "origin", remote_url], cwd=project_path)
            print(Fore.YELLOW + f"📘 Remote repository added: {remote_url}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Git init failed: {e}" + Style.RESET_ALL)


def main():
    args = parse_args()

    project_name = input("📝 Enter project name: ").strip()
    if not project_name:
        print("❌ Project name cannot be empty.")
        return

    project_path = Path.cwd() / project_name
    project_path.mkdir(parents=True, exist_ok=True)

    if args.interactive:
        print("\n🔧 Interactive setup enabled:")
        folders = prompt_folder_creation()
        create_project_structure(project_path, folders)
    else:
        # Set up default folders if interactive setup is not chosen
        default_folders = ["src", "tests", "docs"]
        create_project_structure(project_path, default_folders)

    create_files(project_path, dependencies=args.dependencies)

    if not args.no_venv:
        venv_path = create_venv(project_path, python_version=args.python_version)
        if venv_path:
            activate_virtual_env(venv_path)

    git_choice = input("📘 Do you want to initialize a Git repository? (y/n): ").lower().strip()
    if git_choice == 'y':
        init_git(project_path, remote_url=args.git_remote)

    print(Fore.GREEN + f"\n✅ Project '{project_name}' initialized successfully!" + Style.RESET_ALL)


if __name__ == "__main__":
    main()