import unittest
import sys
import os
from google import genai
import google.api_core.exceptions # Import for error handling

# Add the project root directory to the Python path
# This allows finding both mcp_translator and potentially sibling packages
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Now import should work relative to the project root
from text_splitter import split_text_intelligently

# --- Gemini API Configuration ---
# Configure Gemini API Key from environment variable
API_KEY = os.environ.get("GEMINI_API_KEY")
gemini_client_instance = None # Global client instance
GEMINI_TEST_MODEL = "gemini-2.0-flash" # Match server.py user edit

if API_KEY:
    try:
        # Use the client-based approach
        # genai.configure is not needed when using Client directly with API key
        gemini_client_instance = genai.Client()
        # Optional: Perform a quick check, e.g., list models or a small generation
        # Note: Use the specific model name when generating
        # Example check (can be slow):
        # print(f"Checking model {GEMINI_TEST_MODEL}...")
        # gemini_client_instance.generate_content(model=f"models/{GEMINI_TEST_MODEL}", contents="test")
        print("Gemini Client initialized successfully.")
    except Exception as e:
        print(f"Warning: Failed to initialize Gemini Client: {e}. PDF tests requiring the API will be skipped.")
        gemini_client_instance = None
else:
    print("Warning: GEMINI_API_KEY environment variable not set. PDF tests requiring the API will be skipped.")
# --- End Gemini API Configuration ---


class TestTextSplitting(unittest.TestCase):

    def test_empty_text(self):
        """Test splitting an empty string."""
        text = ""
        chunks = split_text_intelligently(text, 100)
        self.assertEqual(chunks, [], "Should return an empty list for empty text")

    def test_short_text(self):
        """Test splitting text shorter than chunk size."""
        text = "This is a short sentence."
        chunks = split_text_intelligently(text, 100)
        self.assertEqual(chunks, ["This is a short sentence."], "Should return the original text as one chunk")

    def test_english_sentence_split(self):
        """Test splitting at English sentence boundaries."""
        text = "First sentence. Second sentence! Third sentence?"
        chunks = split_text_intelligently(text, 20) # Force splitting
        expected = ["First sentence.", "Second sentence!", "Third sentence?"]
        self.assertEqual(chunks, expected, "Should split at sentence endings")

    def test_chinese_sentence_split(self):
        """Test splitting at Chinese sentence boundaries."""
        text = "第一句话。第二句话！第三句话？"
        chunks = split_text_intelligently(text, 8) # Force splitting (Chinese characters take more space visually)
        expected = ["第一句话。", "第二句话！", "第三句话？"]
        self.assertEqual(chunks, expected, "Should split at Chinese sentence endings")

    def test_mixed_language_split(self):
        """Test splitting text with mixed English and Chinese."""
        text = "Hello world. 你好世界！ Next part."
        chunks = split_text_intelligently(text, 15) # Force splitting
        # Note: Exact splitting depends on punctuation and spacing
        expected = ["Hello world.", "你好世界！", "Next part."]
        self.assertEqual(chunks, expected, "Should handle mixed language punctuation")

    def test_split_at_whitespace(self):
        """Test splitting falls back to whitespace when no sentence ending is near."""
        text = "This is a long string without proper sentence endings just spaces"
        chunks = split_text_intelligently(text, 30)
        # Expecting it to split near the 30 char mark, preferring whitespace
        expected = ["This is a long string without", "proper sentence endings just", "spaces"]
        self.assertEqual(chunks, expected, "Should split at whitespace if no sentence ending is found")

    def test_split_at_chunk_limit(self):
        """Test splitting forces a break if no sentence ending or whitespace is found."""
        text = "LongStringWithoutAnySpacesOrPunctuationAtAll"
        chunks = split_text_intelligently(text, 15)
        expected = ["LongStringWitho", "utAnySpacesOrPu", "nctuationAtAll"]
        self.assertEqual(chunks, expected, "Should split at the character limit if no other break point is found")

    def test_whitespace_handling(self):
        """Test handling of various whitespace scenarios."""
        text = "  Sentence one.  \n\n Sentence two.  End.  "
        chunks = split_text_intelligently(text, 15)
        expected = ["Sentence one.", "Sentence two.", "End."]
        self.assertEqual(chunks, expected, "Should trim whitespace and handle newlines")

    def test_chinese_no_punctuation(self):
        """Test splitting Chinese text without punctuation near the boundary."""
        text = "这是一段没有标点符号的中文长文本用于测试" # Length 20
        chunks = split_text_intelligently(text, 10) # Chunk size 10
        # Expecting a hard break as there is no punctuation and text > chunk_size
        expected = ["这是一段没有标点符号", "的中文长文本用于测试"]
        self.assertEqual(chunks, expected, "Should hard split Chinese text if no punctuation is present and text exceeds chunk size")

    def test_chinese_no_punctuation_no_split(self):
        """Test splitting Chinese text without punctuation near the boundary."""
        text = "这是一段没有标点符号的中文长文本用于测试" # Length 20
        chunks = split_text_intelligently(text, 20) # Chunk size 20
        # Expecting a hard break as there is no punctuation and text > chunk_size
        expected = ["这是一段没有标点符号的中文长文本用于测试"]
        self.assertEqual(chunks, expected, "Should hard split Chinese text if no punctuation is present and text exceeds chunk size")

    def test_specific_file_split(self):
        """Test splitting a specific file and check the number of chunks."""
        file_path = 'test/chinese.txt'
        chunk_size = 1000 # Same as server default
        # !!! PLEASE REPLACE EXPECTED_CHUNK_COUNT with the correct value !!!
        # EXPECTED_CHUNK_COUNT = 2 # The splitter currently splits at newlines/whitespace frequently
        EXPECTED_CHUNK_COUNT = 3 # Updated based on improved splitting

        if not os.path.exists(file_path):
            self.skipTest(f"Test file not found: {file_path}")
            return # Skip the test if the file doesn't exist

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            self.fail(f"Failed to read test file {file_path}: {e}")
            return # Stop test if reading fails

        chunks = split_text_intelligently(text, chunk_size)
        self.assertEqual(len(chunks), EXPECTED_CHUNK_COUNT,
                         f"Expected {EXPECTED_CHUNK_COUNT} chunks for {file_path}, but got {len(chunks)}")


# --- New Test Class for PDF Processing ---
class TestPDFProcessing(unittest.TestCase):

    @unittest.skipIf(not API_KEY or not gemini_client_instance, "GEMINI_API_KEY not set or client initialization failed")
    def test_pdf_extraction_live(self):
        """Test PDF text extraction using the live Gemini API via Client."""
        pdf_path = 'test/academic_paper_figure.pdf'
        self.assertTrue(os.path.exists(pdf_path), f"Test PDF file not found: {pdf_path}")

        # Use the client instance created globally
        
        uploaded_file = None
        try:
            print(f"\nAttempting to upload PDF: {pdf_path}")
            absolute_pdf_path = os.path.abspath(pdf_path)
            if not os.path.exists(absolute_pdf_path):
                 self.fail(f"Absolute path to test PDF not found: {absolute_pdf_path}")

            # Use client.files.upload_file
            uploaded_file = gemini_client_instance.files.upload(
                file=absolute_pdf_path,
                            )
            print(f"Successfully uploaded file: {uploaded_file.name}")

            print(f"Generating content from PDF using model {GEMINI_TEST_MODEL}...")
            prompt = "Extract the text content from this document."
            # Use client.models.generate_content (matching recent server.py change)
            response = gemini_client_instance.models.generate_content(
                model=GEMINI_TEST_MODEL, # Prefix with models/
                contents=[prompt, uploaded_file],
                # request_options={"timeout": 300} # Check Client documentation for timeouts
            )
            print("Received response from Gemini.")

            # Basic check on the response text
            self.assertIsInstance(response.text, str)
            self.assertGreater(len(response.text), 100, "Extracted text seems too short.")
            self.assertIn("Hydrology", response.text, "Expected keyword 'Hydrology' not found in extracted text.")
            print("Text extraction checks passed.")

        except google.api_core.exceptions.GoogleAPIError as api_e:
            import traceback
            self.fail(f"Gemini API error during PDF processing: {api_e}\n{traceback.format_exc()}")
        except Exception as e:
            import traceback
            self.fail(f"PDF processing failed: {e}\n{traceback.format_exc()}")
        finally:
            if uploaded_file:
                try:
                    print(f"Attempting to delete uploaded file: {uploaded_file.name}")
                    # Use client.files.delete_file
                    gemini_client_instance.files.delete(name=uploaded_file.name)
                    print(f"Successfully deleted uploaded file: {uploaded_file.name}")
                except Exception as del_e:
                    print(f"Warning: Could not delete uploaded file {uploaded_file.name}: {del_e}")
# --- End New Test Class ---


if __name__ == '__main__':
    unittest.main() 