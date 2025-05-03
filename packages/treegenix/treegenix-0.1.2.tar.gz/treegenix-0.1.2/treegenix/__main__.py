# treegen/__main__.py

import os
import argparse

def print_tree(startpath, prefix='', excluded=None):
    excluded = set(excluded or [])
    files = sorted(os.listdir(startpath))
    files = [f for f in files if f not in excluded and not f.startswith('.')]

    for index, name in enumerate(files):
        path = os.path.join(startpath, name)
        connector = '├── ' if index < len(files) - 1 else '└── '
        display_name = name + '/' if os.path.isdir(path) else name
        print(prefix + connector + display_name)
        if os.path.isdir(path):
            extension = '│   ' if index < len(files) - 1 else '    '
            print_tree(path, prefix + extension, excluded)

def main():
    parser = argparse.ArgumentParser(description='Generate a clean tree of your project folder.')
    parser.add_argument('path', nargs='?', default='.', help='Path to the folder (default: current directory)')
    parser.add_argument('--exclude', nargs='*', default=[], help='Folders/files to exclude')

    args = parser.parse_args()
    print("```")
    print(os.path.basename(os.path.abspath(args.path)) + '/')
    print_tree(args.path, excluded=args.exclude)
    print("```")
    print("\nMade with ❤️  by Sujal Bhagat")
    print("GitHub: https://github.com/sujal-1245")

if __name__ == "__main__":
    main()
