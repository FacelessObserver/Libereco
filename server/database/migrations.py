from aiosqlite import Connection

class DatabaseMigrations:

    @staticmethod
    async def create_tables(conn: Connection) -> None:
        tables = [
            """
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                public_key BLOB NOT NULL,
                password_hash BLOB NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS chats (
                initiator TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
                copycat TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
                PRIMARY KEY(initiator, copycat)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
                recipient TEXT NOT NULL REFERENCES users(username) ON DELETE CASCADE,
                encrypted_content BLOB NOT NULL,
                received_at TEXT NOT NULL
            )
            """
        ]

        for table in tables:
            await conn.execute(table)
    
    @staticmethod
    async def create_indexes(conn: Connection):
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_messages_recipient ON messages(recipient)",
            "CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender)",
            "CREATE INDEX IF NOT EXISTS idx_messages_received_at ON messages(received_at)",
            "CREATE INDEX IF NOT EXISTS idx_chats_initiator ON chats(initiator)",
            "CREATE INDEX IF NOT EXISTS idx_chats_copycat ON chats(copycat)"
        ]
        
        for index in indexes:
            await conn.execute(index)
    
    @staticmethod
    async def init(conn: Connection) -> None:
        await DatabaseMigrations.create_tables(conn)
        await DatabaseMigrations.create_indexes(conn)
        await conn.commit()
