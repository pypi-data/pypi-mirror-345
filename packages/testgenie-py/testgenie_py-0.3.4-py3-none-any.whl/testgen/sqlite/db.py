import sqlite3

def create_database(db_name="testgen.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TestSuite (
            id INTEGER PRIMARY KEY,
            name TEXT,
            creation_date TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SourceFile (
            id INTEGER PRIMARY KEY,
            path TEXT,
            lines_of_code INTEGER,
            last_modified TIMESTAMP
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Function (
            id INTEGER PRIMARY KEY,
            name TEXT,
            start_line INTEGER,
            end_line INTEGER,
            num_lines INTEGER,
            source_file_id INTEGER,
            FOREIGN KEY (source_file_id) REFERENCES SourceFile(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TestCase (
            id INTEGER PRIMARY KEY,
            name TEXT,
            expected_output TEXT,  -- storing JSON as TEXT
            input TEXT,            -- storing JSON as TEXT
            test_function TEXT,
            last_run_time TIMESTAMP,
            test_method_type INTEGER,
            test_suite_id INTEGER,
            function_id INTEGER,
            FOREIGN KEY (test_suite_id) REFERENCES TestSuite(id),
            FOREIGN KEY (function_id) REFERENCES Function(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TestResult (
            id INTEGER PRIMARY KEY,
            test_case_id INTEGER,
            status BOOLEAN,
            error TEXT,
            execution_time TIMESTAMP,
            FOREIGN KEY (test_case_id) REFERENCES TestCase(id)
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS CoverageData (
            id INTEGER PRIMARY KEY,
            file_name TEXT,
            executed_lines INTEGER,
            missed_lines INTEGER,
            branch_coverage REAL,
            source_file_id INTEGER,
            FOREIGN KEY (source_file_id) REFERENCES SourceFile(id)
        );
    """)

    conn.commit()
    conn.close()
    print(f"Database '{db_name}' created successfully with all tables.")

if __name__ == "__main__":
    create_database()
