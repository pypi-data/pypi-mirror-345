import os
import subprocess
import argparse

README_TEMPLATE = """# {name}

A simple Python package.
"""

SETUP_TEMPLATE = '''from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="{name}",
    version="0.1.0",
    author="{username}",
    author_email="{username}.contact@gmail.com",
    description="A simple Python package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/{username}/{name}",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
'''

LICENSE_TEMPLATE = """MIT License

Copyright (c) 2025 {username}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

INIT_TEMPLATE = '''__version__ = "0.1.0"
'''

CODE_TEMPLATE = '''def example():
    print("Hello from {pkg_name}!")
'''

def build(args):
    """Build the package."""
    os.chdir(args.path)

    if args.tar:
        print("Building source distribution...")
        subprocess.run(['python', 'setup.py', 'sdist'])

    if args.whl:
        print("Building wheel distribution...")
        subprocess.run(['python', 'setup.py', 'bdist_wheel'])

    if not (args.tar or args.whl):
        print("Please specify --tar and/or --whl.")

def init(args):
    """Initialize a new Python package layout."""
    if os.path.exists(args.name):
        print(f"Directory '{args.name}' already exists.")
        return

    os.makedirs(f"{args.name}/{args.name}")

    with open(f"{args.name}/README.md", "w") as f:
        f.write(README_TEMPLATE.format(name=args.name))

    with open(f"{args.name}/LICENSE", "w") as f:
        f.write(LICENSE_TEMPLATE.format(username=args.username))

    with open(f"{args.name}/setup.py", "w") as f:
        f.write(SETUP_TEMPLATE.format(name=args.name, username=args.username))

    with open(f"{args.name}/{args.name}/__init__.py", "w") as f:
        f.write(INIT_TEMPLATE)

    with open(f"{args.name}/{args.name}/code.py", "w") as f:
        f.write(CODE_TEMPLATE.format(pkg_name=args.name))

    print(f"Initialized new package '{args.name}' for user '{args.username}' at './{args.name}'.")

def install(args):
    """Install the package locally."""
    if not os.path.exists(args.path):
        print(f"Path '{args.path}' does not exist.")
        return

    print(f"Installing package from '{args.path}'...")
    result = subprocess.run(['pip', 'install', args.path])
    if result.returncode == 0:
        print("Package installed successfully.")
    else:
        print("Installation failed.")

def main():
    parser = argparse.ArgumentParser(description="BuildSnap CLI.")

    subparsers = parser.add_subparsers()

    # Build Command
    build_parser = subparsers.add_parser('build', help="Build the package.")
    build_parser.add_argument('--tar', action='store_true', help='Build source distribution (.tar.gz).')
    build_parser.add_argument('--whl', action='store_true', help='Build wheel distribution (.whl).')
    build_parser.add_argument('--path', '-p', default='.', help='Path to setup.py or project root.')
    build_parser.set_defaults(func=build)

    # Init Command
    init_parser = subparsers.add_parser('init', help="Initialize a new Python package layout.")
    init_parser.add_argument('--name', required=True, help='Package name to initialize.')
    init_parser.add_argument('--username', required=True, help='Your GitHub username (also used in LICENSE and setup).')
    init_parser.set_defaults(func=init)

    # Install Command
    install_parser = subparsers.add_parser('install', help="Install the package locally.")
    install_parser.add_argument('--path', '-p', default='.', help='Path to the package directory to install.')
    install_parser.set_defaults(func=install)

    # Parse arguments and call the corresponding function
    args = parser.parse_args()

    # Ensure func exists before calling it
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()