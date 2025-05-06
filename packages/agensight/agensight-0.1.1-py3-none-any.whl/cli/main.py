# fault/cli.py

import argparse
import webbrowser
from agensight.server import start_server

def view_project():
    start_server()
    webbrowser.open("http://localhost:5000")

def main():
    parser = argparse.ArgumentParser(prog="agensight")
    subparsers = parser.add_subparsers(dest="command")

    view_parser = subparsers.add_parser("view", help="View the agensight project")

    args = parser.parse_args()
    if args.command == "view":
        view_project()
    else:
        parser.print_help()