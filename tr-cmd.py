#!python
#!/usr/bin/env python3

import sys
import os
from tableRoller import Table, debug

def main():
    if len(sys.argv) < 3:
        print("Usage: tr-cmd.py <table_query> <data_dir> [additional_data_dirs...]")
        sys.exit(1)

    table_query = sys.argv[1]
    data_dirs = sys.argv[2:]

    # Load all table files from the specified directories
    for data_dir in data_dirs:
        for root, _, files in os.walk(data_dir):
            for file in files:
                if file.endswith('.txt'):
                    Table.parseFile(os.path.join(root, file))

    try:
        # Generate and print the result
        result = Table.resultsAsString(table_query)
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()