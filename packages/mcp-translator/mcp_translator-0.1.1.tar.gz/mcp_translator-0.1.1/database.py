import sqlite3
import logging

logger = logging.getLogger(__name__)

def initialize_db(db_path: str) -> sqlite3.Connection:
    """Initializes the SQLite database and creates the chunks table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            original_text TEXT NOT NULL,
            translated_text TEXT,
            is_translated BOOLEAN DEFAULT FALSE
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_path_is_translated ON chunks (file_path, is_translated)')
    conn.commit()
    logger.info("Database table 'chunks' ensured to exist with 'file_path' column and index.")
    return conn

def clear_db_for_file(conn: sqlite3.Connection, file_path: str):
    """Clears entries from the chunks table for a specific file_path."""
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM chunks WHERE file_path = ?', (file_path,))
        conn.commit()
        logger.info(f"Cleared previous entries for file '{file_path}' from the 'chunks' table.")
    except sqlite3.Error as e:
        logger.error(f"Error clearing database for file {file_path}: {e}")
        conn.rollback() # Rollback in case of error

def add_chunks(conn: sqlite3.Connection, file_path: str, chunks: list[str]) -> int:
    """Adds a list of text chunks to the database, associated with a file_path."""
    cursor = conn.cursor()
    try:
        cursor.executemany(
            'INSERT INTO chunks (file_path, original_text) VALUES (?, ?)',
            [(file_path, chunk) for chunk in chunks]
        )
        conn.commit()
        logger.info(f"Added {len(chunks)} new chunks for file '{file_path}' to the database.")
        return len(chunks)
    except sqlite3.Error as e:
        logger.error(f"Error adding chunks for file {file_path}: {e}")
        conn.rollback()
        return 0

def get_next_untranslated_chunk(conn: sqlite3.Connection, file_path: str) -> tuple | None:
    """Retrieves the next chunk for a specific file_path that hasn't been translated."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            'SELECT id, original_text FROM chunks WHERE file_path = ? AND is_translated = FALSE ORDER BY id ASC LIMIT 1',
            (file_path,)
        )
        chunk = cursor.fetchone()
        return chunk
    except sqlite3.Error as e:
        logger.error(f"Error fetching next untranslated chunk for file {file_path}: {e}")
        return None

def update_chunk_translation(conn: sqlite3.Connection, chunk_id: int, translated_text: str) -> bool:
    """Updates a chunk with its translated text and marks it as translated."""
    cursor = conn.cursor()
    try:
        cursor.execute(
            'UPDATE chunks SET translated_text = ?, is_translated = TRUE WHERE id = ? AND is_translated = FALSE',
            (translated_text, chunk_id)
        )
        updated_rows = cursor.rowcount
        conn.commit()
        if updated_rows > 0:
            logger.debug(f"Updated chunk {chunk_id} with translation.")
            return True
        else:
            # Check if the chunk ID exists but was already translated or doesn't exist
            cursor.execute('SELECT is_translated FROM chunks WHERE id = ?', (chunk_id,))
            result = cursor.fetchone()
            if result is None:
                logger.warning(f"Chunk ID {chunk_id} not found.")
            elif result[0]:
                logger.warning(f"Chunk {chunk_id} was already translated. No update performed.")
            else:
                 # This case should theoretically not happen if updated_rows was 0 and the chunk exists and is not translated
                 logger.warning(f"Could not update chunk ID {chunk_id} for an unknown reason.")
            return False
    except sqlite3.Error as e:
        logger.error(f"Error updating chunk {chunk_id}: {e}")
        conn.rollback()
        return False

def get_file_path_for_chunk(conn: sqlite3.Connection, chunk_id: int) -> str | None:
    """Retrieves the file_path associated with a given chunk_id."""
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT file_path FROM chunks WHERE id = ?', (chunk_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        logger.error(f"Error getting file_path for chunk {chunk_id}: {e}")
        return None

def get_untranslated_count(conn: sqlite3.Connection, file_path: str) -> int:
    """Gets the count of untranslated chunks for a given file."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM chunks
        WHERE file_path = ? AND is_translated = 0
    """, (file_path,))
    result = cursor.fetchone()

    if result is None: # Should ideally check if the file exists at all first
        cursor.execute('SELECT 1 FROM chunks WHERE file_path = ? LIMIT 1', (file_path,))
        if not cursor.fetchone():
            return -1 # Indicate file not found or no chunks exist
        else: # File exists, but no untranslated chunks
            return 0
    return result[0]

def get_all_translated_chunks(conn: sqlite3.Connection, file_path: str) -> list[str] | None:
    """Retrieves all translated chunks for a given file in order."""
    cursor = conn.cursor()
    # First, check if all chunks are translated
    untranslated_count = get_untranslated_count(conn, file_path)
    if untranslated_count > 0:
        logger.warning(f"Attempted to retrieve all chunks for '{file_path}' but {untranslated_count} are untranslated.")
        return None # Not all chunks are translated
    elif untranslated_count == -1:
        logger.error(f"File '{file_path}' not found in database for chunk retrieval.")
        return None # File not found or no chunks

    # If all are translated (or count is 0 and file exists), retrieve them
    cursor.execute("""
        SELECT translated_text
        FROM chunks
        WHERE file_path = ? AND is_translated = 1
        ORDER BY id ASC
    """, (file_path,))
    results = cursor.fetchall()
    if not results: # Could happen if file was empty or had 0 chunks initially
         # Check if the file actually exists in the db
         cursor.execute('SELECT 1 FROM chunks WHERE file_path = ? LIMIT 1', (file_path,))
         if not cursor.fetchone():
             logger.error(f"File '{file_path}' not found when retrieving chunks, though untranslated count was 0.")
             return None # File doesn't exist after all
         else:
             logger.info(f"File '{file_path}' exists but has no translated chunks (possibly empty initially).")
             return [] # Return empty list for empty file

    # Extract the text from each tuple
    translated_chunks = [row[0] for row in results]
    return translated_chunks

def list_translation_jobs(conn: sqlite3.Connection) -> list[dict]:
    """Lists all distinct translation jobs (file_paths) and their progress."""
    cursor = conn.cursor()
    jobs = []
    try:
        cursor.execute('SELECT DISTINCT file_path FROM chunks')
        file_paths = [row[0] for row in cursor.fetchall()]

        for file_path in file_paths:
            cursor.execute('SELECT COUNT(*) FROM chunks WHERE file_path = ?', (file_path,))
            total_chunks = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM chunks WHERE file_path = ? AND is_translated = TRUE', (file_path,))
            translated_chunks = cursor.fetchone()[0]
            jobs.append({
                "file_path": file_path,
                "total_chunks": total_chunks,
                "translated_chunks": translated_chunks,
                "progress_percent": round((translated_chunks / total_chunks) * 100, 2) if total_chunks > 0 else 0
            })
        return jobs
    except sqlite3.Error as e:
        logger.error(f"Error listing translation jobs: {e}")
        return [] 