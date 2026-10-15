import sqlite3


def create_database():

    connection = sqlite3.connect("blood_finder.db")

    cursor = connection.cursor()


    # Create donors table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donors (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            phone TEXT NOT NULL,

            blood_group TEXT NOT NULL,

            location TEXT NOT NULL,

            last_donation TEXT NOT NULL,

            availability TEXT NOT NULL

        )
    """)


    # Add verification column if it doesn't already exist
    cursor.execute("""
        PRAGMA table_info(donors)
    """)

    columns = [column[1] for column in cursor.fetchall()]


    if "verification_status" not in columns:

        cursor.execute("""
            ALTER TABLE donors
            ADD COLUMN verification_status TEXT DEFAULT 'Pending'
        """)


    connection.commit()

    connection.close()


if __name__ == "__main__":

    create_database()

    print("Database updated successfully!")
    