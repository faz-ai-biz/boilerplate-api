#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

VERSION_FILE = "version.txt"


def read_version():
    try:
        with open(VERSION_FILE, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "0.1.0"


def write_version(version):
    with open(VERSION_FILE, "w") as f:
        f.write(version)


def bump_version(version_part):
    current = read_version()
    major, minor, patch = map(int, current.split("."))

    if version_part == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_part == "minor":
        minor += 1
        patch = 0
    elif version_part == "patch":
        patch += 1

    new_version = f"{major}.{minor}.{patch}"
    write_version(new_version)
    return new_version


def main():
    parser = argparse.ArgumentParser(description="Version management tool")
    parser.add_argument("action", choices=["get", "bump"])
    parser.add_argument(
        "--part", choices=["major", "minor", "patch"], help="Version part to bump"
    )

    args = parser.parse_args()

    if args.action == "get":
        print(read_version())
    elif args.action == "bump":
        if not args.part:
            parser.error("--part is required for bump action")
        new_version = bump_version(args.part)
        print(f"Version bumped to {new_version}")


if __name__ == "__main__":
    main()
