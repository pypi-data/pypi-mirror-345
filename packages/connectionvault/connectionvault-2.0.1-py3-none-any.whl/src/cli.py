
from .connection_manager import main as conn_manage_main
import argparse
import os

# Hardcoded version information
VERSION = "2.0.1"

# Hardcoded dependencies information
DEPENDENCIES = {
    "python": "^3.11",
    "PyYAML": "^6.0.2",
    "SQLAlchemy": "^2.0.36",
    "psycopg2": "^2.9.10",
    "pandas": "^2.2.3",
    "pyodbc": "^5.2.0",
    "pylint": "^3.3.1",
    "mysql-connector-python": "^9.3.0",
    "poetry": "^1.8.4"
}

# Hardcoded usage information
EXAMPLE = """

ENSURE YOU HAVE SET THE ENVIRONMENT VARIABLE 'conn_home' TO THE DIRECTORY WHERE YOUR connections.yaml FILE IS LOCATED.

Sample Usage 1: Interactive with User Input

from src.connection_utility import (load_connections, choose_connection)
from sqlalchemy import create_engine
import pandas as pd

def main():
    connections = load_connections()
    conn = choose_connection(connections)

    engine = create_engine(conn)
    query = input("Input your query: ")
    df = pd.read_sql_query(query, engine)
    print(df)

if __name__ == "__main__":
    main()```

Sample Usage 2: Code for a Specific Connection, suitable for batch cycle jobs.

conn_home = os.environ.get('conn_home')
connection_file = os.path.join(conn_home, 'connection.yaml')

with open("connection_file", "r") as file:
    connections = yaml.safe_load(file)

connection_detail = connections['CONFIG IN CONNECTIONS.YAML']
CONNECTION_STRING = make_string(connection_detail)

"""

def main():
    parser = argparse.ArgumentParser(description='ConnectionVault CLI Tool')
    parser.add_argument('--version', action='version', version=f'ConnectionVault {VERSION}')
    parser.add_argument('--dependencies', action='store_true', help='Show project dependencies')
    parser.add_argument('--example', action='store_true', help='Show sample code syntax')
    parser.add_argument('--connections', action='store_true', help='Start connection manager utility')
    parser.add_argument('--yamldir', action='store_true', help='Show location of connection.yaml file')

    
    args = parser.parse_args()

    if args.dependencies:
        print("Project Dependencies:")
        for dep, version in DEPENDENCIES.items():
            print(f"{dep}: {version}")

    if args.example:
        print("Usage Information:\n")
        print(EXAMPLE)

    if args.connections:
        conn_manage_main()

    if args.yamldir:
        conn_home = os.getenv('conn_home')
        if conn_home:
            print(f"conn_home: {conn_home}")
        else:
            print("please set conn_home variable")

if __name__ == '__main__':
    main()

