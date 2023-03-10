import sqlite3


def execute(query, params=None):
    # Connect to the database
    conn = sqlite3.connect('chatdata.db')

    # Create a cursor object
    cursor = conn.cursor()

    # Execute the query
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()
    return cursor.lastrowid


def get_results(query, params=None):
    # Connect to the database
    conn = sqlite3.connect('chatdata.db')

    # Create a cursor object
    cursor = conn.cursor()

    # Execute the query
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    # Fetch all the rows as a list of tuples
    rows = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Return the rows
    return rows


def get_scalar(query, params=None):
    # Connect to the database
    conn = sqlite3.connect('chatdata.db')

    # Create a cursor object
    cursor = conn.cursor()

    # Execute the query
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)

    # Fetch the first row
    row = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # Return the first column of the first row
    return row[0]
