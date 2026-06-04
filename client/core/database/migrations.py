from aiosqlite import Connection

class DatabaseMigrations:

    @staticmethod
    async def create_tables(conn: Connection):
        tables = [
            """
            CREATE TABLE IF NOT EXISTS identity (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                display_name TEXT,
                private_key BLOB NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS sessions (
                interlocutor TEXT PRIMARY KEY,
                shared_secret BLOB NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS messages (
                sender TEXT NOT NULL,
                recipient TEXT NOT NULL,
                content BLOB NOT NULL,
                received_at TEXT NOT NULL
            )
            """
        ]

        for table in tables:
            await conn.execute(table)
    
    @staticmethod
    async def create_indexes(conn: Connection):
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_msg_sender ON messages(sender)",
            "CREATE INDEX IF NOT EXISTS idx_msg_recipient ON messages(recipient)",
            "CREATE INDEX IF NOT EXISTS idx_msg_time ON messages(received_at)"
        ]

        for index in indexes:
            await conn.execute(index)
    
    @staticmethod
    async def init(conn: Connection) -> None:
        await DatabaseMigrations.create_tables(conn)
        await DatabaseMigrations.create_indexes(conn)
        await conn.commit()
