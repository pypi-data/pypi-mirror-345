# Django Project Initializer
# by: AdrianJames27

import os
import stat
import subprocess
import shutil
import sys
import signal

def remove_readonly(func, path, exc_info):
    """
    Error handler for shutil.rmtree.

    Clears the readonly bit and reattempts removal.
    """
    os.chmod(path, stat.S_IWRITE)  # Add write permission
    func(path)

def prompt_for_project_name():
    """
    Prompt the user for a project name, ensuring it's not empty.
    Use current directory if input is '.'.
    """
    while True:
        try:
            project_name = input("Enter the project name (or '.' for current directory): ").strip()
            
            if not project_name:
                print("Project name cannot be empty. Please enter a valid name.")
                continue

            return project_name
        except KeyboardInterrupt:
            print("\nProcess interrupted during input. Exiting...")
            sys.exit(0)

def clone_repository(project_name):
    """
    Clone the template repo into `project_name` or current directory if '.'.
    """
    repo_url = "https://github.com/AdrianJames27/django_template.git"

    # Determine target directory for cloning
    target_dir = os.getcwd() if project_name == '.' else project_name
    
    subprocess.run([
        "git", "clone", "--depth", "1", "--branch", "master", repo_url, target_dir
    ], check=True)
    
    return target_dir

def remove_git_directory(clone_dir):
    """
    Remove the .git directory from the cloned repository.
    """
    git_dir = os.path.join(clone_dir, ".git")

    if os.path.exists(git_dir):
        shutil.rmtree(git_dir, onexc=remove_readonly)

def handle_sigint(*_):
    print('\nProcess interrupted (Ctrl+C). Exiting...')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, handle_sigint)

    try:
        project_name = prompt_for_project_name()
        clone_dir = clone_repository(project_name)
        remove_git_directory(clone_dir)

        if project_name == ".":
            print("\nProject has been initialized in the current directory.")
        else:
            print(f"\nProject '{project_name}' has been initialized successfully.")

        print("\nNext steps:")
        print("1. Install pipenv if not already installed:")
        print("   pip install pipenv")

        if project_name != ".":
            print("2. Change directory to your project:")
            print(f"   cd {project_name}")
        else:
            print("2. Ensure you are in your project directory (current directory).")
        
        print("3. Activate the virtual environment:")
        print("   pipenv shell")
        print("4. Install the required packages:")
        print("   pipenv install -r requirements.txt")
        print("5. Run the development server:")
        print("   py manage.py runserver")
        print()

    except EOFError:
        print("\nInput ended. Exiting...")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\nGit command failed with error: {e}. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}. Exiting...")
        sys.exit(1)

if __name__ == "__main__":
    main()
