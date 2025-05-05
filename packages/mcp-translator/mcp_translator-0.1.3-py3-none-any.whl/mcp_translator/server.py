import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import click
from mcp.server.fastmcp import FastMCP
# import mcp.types as types # Not currently used
import sqlite3
import os
from mcp_translator import database # Use relative import
from mcp_translator.text_splitter import split_text_intelligently # Import the function
from google import genai

# Configure the Gemini API key (ideally through environment variables)
# genai.configure(api_key="YOUR_API_KEY") # Placeholder - API key management needed

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__) or '.', "translation_progress.db")
# Default values, can be overridden by CLI args
CHUNK_SIZE = 1000  # Characters per chunk
GEMINI_MODEL_NAME = "gemini-2.0-flash" # Default Gemini model

# Global variable for the database connection
db_conn: sqlite3.Connection | None = None
# Global variable for the Gemini client
genai_client: genai.client.Client | None = None


@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[None]: # Changed yield type
    """Manage database and Gemini client lifecycle."""
    global db_conn, genai_client # Declare intent to modify global variables
    logger.info("Starting server lifespan...")
    # Ensure the directory for the DB exists if it's relative
    db_dir = os.path.dirname(DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"Created directory for database: {db_dir}")

    db_conn = database.initialize_db(DB_PATH) # Assign to global variable
    logger.info(f"Database initialized at {DB_PATH}")

    try:
        logger.info("Initializing Gemini Client...")
        genai_client = genai.Client()
        # You might add a check here to see if the client initialized correctly
        # e.g., by listing models, but it might add startup latency.
        logger.info("Gemini Client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini Client: {e}. PDF processing will be unavailable.")
        # Decide if the server should proceed without the client
        genai_client = None # Ensure it's None if initialization fails

    try:
        yield # No state needs to be yielded
    finally:
        logger.info("Closing database connection...")
        if db_conn:
            db_conn.close()
            db_conn = None # Clear the global variable
        # Gemini client doesn't typically require explicit closing for simple use cases
        logger.info("Server lifespan ended.")

mcp = FastMCP(
    "TranslatorServer",
    lifespan=server_lifespan,
    dependencies=["sqlite3", "pydantic", "google-generativeai"] # Add google-generativeai
)

# --- Helper Function for Text Splitting ---

# Moved to text_splitter.py
# def split_text_intelligently(text: str, chunk_size: int) -> list[str]:
#     ... (removed function body) ...
#     return chunks

# --- Tool Implementations ---

@mcp.tool()
async def start_translation(file_path: str) -> dict:
    """
    Initializes or restarts the translation process for a given text or PDF file.
    If the file was processed before, its previous progress will be cleared.
    Extracts text (from PDF if necessary), splits it into chunks, and stores them.

    Args:
        file_path: The path to the text or PDF file to be translated.

    Returns:
        A dictionary indicating success or failure, and the number of chunks created.
    """
    global db_conn, genai_client # Access the global connection and client
    if not db_conn:
        logger.error("Database connection not available.")
        return {"error": "Database connection not available."}

    absolute_file_path = os.path.abspath(file_path)
    logger.info(f"Received request to start translation for: {absolute_file_path}")
    if not os.path.exists(absolute_file_path):
        logger.error(f"File not found: {absolute_file_path}")
        return {"error": f"File not found: {absolute_file_path}"}

    text = ""
    uploaded_file = None # Initialize outside the try block for cleanup
    try:
        if absolute_file_path.lower().endswith(".pdf"):
            if not genai_client:
                logger.error("Gemini client not available. Cannot process PDF.")
                return {"error": "PDF processing unavailable: Gemini client not initialized."}

            logger.info(f"Processing PDF file: {absolute_file_path}")
            # It's better to handle potential API errors during upload/generation
            try:
                logger.info(f"Uploading PDF {absolute_file_path} to Gemini...")
                # Use client.files.upload
                uploaded_file = genai_client.files.upload(
                    file=absolute_file_path,
                )
                logger.info(f"File uploaded successfully: Name={uploaded_file.name}, URI={uploaded_file.uri}")

                # Add a timeout to the generation request? The client might handle this differently.
                # Check client.models.generate_content documentation if timeouts are needed.
                logger.info(f"Generating content from PDF using model {GEMINI_MODEL_NAME}...")
                # Use client.models.generate_content
                response = genai_client.models.generate_content( # Use generate_content directly on the client
                    model=GEMINI_MODEL_NAME, # Model name needs 'models/' prefix
                    contents=[
                        "Extract the text content from this document.", # Prompt first
                        uploaded_file # Then the file object
                    ]
                    # request_options={"timeout": 600} # Example timeout, check API
                )
                # Consider potential Parts and safety ratings if applicable
                text = response.text
                logger.info(f"Successfully extracted text from PDF: {absolute_file_path} (Length: {len(text)})")

            except Exception as pdf_e:
                 logger.error(f"Error processing PDF {absolute_file_path} with Gemini: {pdf_e}")
                 return {"error": f"Could not process PDF file with Gemini: {pdf_e}"}
            finally:
                 # Clean up the uploaded file regardless of success/failure in generation
                 if uploaded_file:
                     try:
                         logger.info(f"Deleting uploaded file: {uploaded_file.name}")
                         # Use client.files.delete
                         genai_client.files.delete_file(name=uploaded_file.name)
                         logger.info(f"Cleaned up uploaded file: {uploaded_file.name}")
                     except Exception as del_e:
                         logger.warning(f"Could not delete uploaded file {uploaded_file.name}: {del_e}")

        else:
            logger.info(f"Reading plain text file: {absolute_file_path}")
            with open(absolute_file_path, 'r', encoding='utf-8') as f:
                text = f.read()
    except Exception as e:
        logger.error(f"Error reading or processing file {absolute_file_path}: {e}")
        # Ensure cleanup if upload happened before another error
        if uploaded_file:
             try:
                 logger.info(f"Deleting uploaded file after error: {uploaded_file.name}")
                 genai_client.files.delete_file(name=uploaded_file.name)
                 logger.info(f"Cleaned up uploaded file: {uploaded_file.name}")
             except Exception as del_e:
                 logger.warning(f"Could not delete uploaded file {uploaded_file.name} after error: {del_e}")
        return {"error": f"Could not read or process file: {e}"}

    if not text and absolute_file_path.lower().endswith(".pdf"):
        logger.warning(f"PDF processing for {absolute_file_path} resulted in empty text.")
        # Optionally return a specific error if PDF text extraction failed silently
        # return {"error": f"Failed to extract text from PDF: {absolute_file_path}", "file_path": absolute_file_path}


    # Use the global db_conn
    database.clear_db_for_file(db_conn, absolute_file_path)

    # Split text using the new function
    # chunks = [text[i:i+CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
    chunks = split_text_intelligently(text, CHUNK_SIZE)

    if not chunks:
        logger.warning(f"Text splitting resulted in zero chunks for file: {absolute_file_path}")
        # Decide how to handle empty chunks, maybe return an error or a specific message
        return {"success": True, "message": f"File '{absolute_file_path}' contained no processable text or could not be split.", "num_chunks": 0, "file_path": absolute_file_path}

    num_chunks = database.add_chunks(db_conn, absolute_file_path, chunks)

    logger.info(f"Successfully split file '{absolute_file_path}' into {num_chunks} chunks using intelligent splitting.")
    return {"success": True, "message": f"File '{absolute_file_path}' processed into {num_chunks} chunks.", "num_chunks": num_chunks, "file_path": absolute_file_path}


@mcp.tool()
async def get_next_chunk(file_path: str) -> dict:
    """
    Fetches the next untranslated text chunk for a specific file.

    Args:
        file_path: The path of the file whose next chunk is needed.

    Returns:
        A dictionary containing the chunk_id, text, and file_path of the next chunk,
        or a message if all chunks for that file are translated or the file is unknown.
    """
    global db_conn # Access the global connection
    if not db_conn:
        logger.error("Database connection not available.")
        return {"error": "Database connection not available."}

    absolute_file_path = os.path.abspath(file_path)
    logger.info(f"Fetching next untranslated chunk for file: {absolute_file_path}")
    # Use the global db_conn
    chunk = database.get_next_untranslated_chunk(db_conn, absolute_file_path)

    if chunk:
        logger.info(f"Returning chunk ID: {chunk[0]} for file '{absolute_file_path}'")
        return {"chunk_id": chunk[0], "text": chunk[1], "file_path": absolute_file_path}
    else:
        # Use the global db_conn
        remaining = database.get_untranslated_count(db_conn, absolute_file_path)
        if remaining == 0:
             logger.info(f"No more untranslated chunks found for file '{absolute_file_path}'.")
             return {"message": f"All chunks have been processed for '{absolute_file_path}'.", "file_path": absolute_file_path}
        elif remaining == -1: # Indicates an error, likely file not found in DB
             logger.warning(f"File '{absolute_file_path}' not found in the translation database.")
             return {"error": f"Translation job for file '{absolute_file_path}' not found. Use start_translation first.", "file_path": absolute_file_path}
        else: # Should not happen if chunk is None and remaining > 0
             logger.error(f"Inconsistent state for file '{absolute_file_path}': get_next_chunk returned None but remaining count is {remaining}")
             return {"error": "Internal server error fetching next chunk.", "file_path": absolute_file_path}

@mcp.tool()
async def submit_translation(chunk_id: int, translated_text: str) -> dict:
    """
    Submits the translated text for a specific chunk ID.

    Args:
        chunk_id: The ID of the chunk that was translated.
        translated_text: The translated text content.

    Returns:
        A dictionary indicating the success or failure of the submission and remaining chunks for the associated file.
    """
    global db_conn # Access the global connection
    if not db_conn:
        logger.error("Database connection not available.")
        return {"error": "Database connection not available."}

    logger.info(f"Received translation for chunk ID: {chunk_id}")

    # Use the global db_conn
    file_path = database.get_file_path_for_chunk(db_conn, chunk_id)
    if not file_path:
        logger.warning(f"Could not find file path for chunk ID: {chunk_id}. Update failed.")
        return {"success": False, "error": f"Chunk ID {chunk_id} not found."}

    # Use the global db_conn
    success = database.update_chunk_translation(db_conn, chunk_id, translated_text)

    if success:
        logger.info(f"Successfully updated translation for chunk ID: {chunk_id} (File: '{file_path}')")
        # Use the global db_conn
        remaining = database.get_untranslated_count(db_conn, file_path)
        if remaining == 0:
             message = f"Translation submitted successfully for chunk {chunk_id}. All chunks complete for file '{file_path}'!"
        elif remaining > 0:
             message = f"Translation submitted successfully for chunk {chunk_id}. {remaining} chunks remaining for file '{file_path}'."
        else: # Should not happen after successful update
            message = f"Translation submitted successfully for chunk {chunk_id}. Error checking remaining count for '{file_path}'."
        return {"success": True, "message": message, "file_path": file_path, "remaining_chunks_for_file": remaining}
    else:
        # Use the global db_conn
        logger.warning(f"Failed to update translation for chunk ID: {chunk_id} (File: '{file_path}').")
        cursor = db_conn.cursor()
        cursor.execute('SELECT is_translated FROM chunks WHERE id = ?', (chunk_id,))
        result = cursor.fetchone()
        error_msg = f"Failed to submit translation for chunk ID {chunk_id}."
        if result and result[0]:
            error_msg = f"Chunk ID {chunk_id} has already been translated."
        elif result is None:
             error_msg = f"Chunk ID {chunk_id} not found."

        return {"success": False, "error": error_msg, "file_path": file_path}

@mcp.tool()
async def list_jobs() -> dict:
    """
    Lists all translation jobs currently tracked by the server and their progress.

    Returns:
        A dictionary containing a list of job statuses.
    """
    global db_conn # Access the global connection
    if not db_conn:
        logger.error("Database connection not available.")
        return {"error": "Database connection not available."}

    logger.info("Request received to list translation jobs.")
    # Use the global db_conn
    jobs = database.list_translation_jobs(db_conn)
    logger.info(f"Found {len(jobs)} translation jobs.")
    return {"jobs": jobs}

@mcp.tool()
async def export_translation(file_path: str) -> dict:
    """
    Exports the complete translated text for a given file if all chunks are translated.

    Args:
        file_path: The path of the original file whose translation should be exported.

    Returns:
        A dictionary containing the path to the exported file upon success,
        or an error message if the translation is incomplete or the job is not found.
    """
    global db_conn
    if not db_conn:
        logger.error("Database connection not available for export.")
        return {"error": "Database connection not available."}

    absolute_file_path = os.path.abspath(file_path)
    logger.info(f"Request received to export translation for: {absolute_file_path}")

    # Check if translation is complete using the existing function
    remaining_count = database.get_untranslated_count(db_conn, absolute_file_path)

    if remaining_count > 0:
        logger.warning(f"Export failed for '{absolute_file_path}': {remaining_count} chunks still untranslated.")
        return {"error": f"Translation is not complete for '{absolute_file_path}'. {remaining_count} chunks remaining.", "file_path": absolute_file_path}
    elif remaining_count == -1:
        logger.error(f"Export failed: Translation job for '{absolute_file_path}' not found.")
        return {"error": f"Translation job for '{absolute_file_path}' not found.", "file_path": absolute_file_path}
    elif remaining_count < -1: # Should not happen, indicates DB error
        logger.error(f"Export failed due to database error checking status for '{absolute_file_path}'.")
        return {"error": "Internal server error checking translation status.", "file_path": absolute_file_path}

    # If remaining_count is 0, proceed to fetch all chunks
    logger.info(f"All chunks translated for '{absolute_file_path}'. Proceeding with export.")
    translated_chunks = database.get_all_translated_chunks(db_conn, absolute_file_path)

    if translated_chunks is None:
        # This case should ideally be caught by remaining_count == -1, but double-check
        logger.error(f"Export failed: Could not retrieve translated chunks for '{absolute_file_path}', possibly file not found.")
        return {"error": f"Could not retrieve translation data for '{absolute_file_path}'.", "file_path": absolute_file_path}

    full_translation = "".join(translated_chunks)

    # Construct output file path
    base, ext = os.path.splitext(absolute_file_path)
    output_file_path = f"{base}_translated{ext}"

    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(full_translation)
        logger.info(f"Successfully exported translation for '{absolute_file_path}' to '{output_file_path}'")
        return {"success": True, "message": f"Translation exported successfully.", "exported_file": output_file_path}
    except Exception as e:
        logger.error(f"Error writing exported file '{output_file_path}': {e}")
        return {"error": f"Could not write exported file: {e}", "file_path": absolute_file_path}

# --- Main Execution ---

@click.command()
@click.option(
    '--chunk-size',
    default=CHUNK_SIZE,
    type=int,
    help='Number of characters per text chunk for processing.',
    show_default=True
)
@click.option(
    '--model',
    default=GEMINI_MODEL_NAME,
    type=str,
    help='The Gemini model name to use for PDF text extraction.',
    show_default=True
)
def main(chunk_size: int, model_name: str) -> int:
    """Starts the Translator Server."""
    global CHUNK_SIZE, GEMINI_MODEL_NAME # Allow modification of globals
    CHUNK_SIZE = chunk_size
    GEMINI_MODEL_NAME = model_name
    logger.info(f"Starting Translator Server with Chunk Size: {CHUNK_SIZE}, Model: {GEMINI_MODEL_NAME}")
    mcp.run()

if __name__ == "__main__":
    main() 