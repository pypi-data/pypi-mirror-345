import re
import logging

# Setup logger
logger = logging.getLogger(__name__)

# Define sentence ending punctuation for various languages
# Added common Chinese punctuation and ensure proper escaping
# SENTENCE_ENDINGS = re.compile(r\'([.!?。！？])(\\s+|$)\') # Old version
SENTENCE_ENDINGS = re.compile(r'[.!?。！？]') # Corrected raw string
# Define potential fallback split points (whitespace)
WHITESPACE = re.compile(r'\s+') # Corrected raw string

def split_text_intelligently(text: str, chunk_size: int) -> list[str]:
    """
    Splits text into chunks, prioritizing sentence boundaries, then whitespace,
    and finally hard character limits.
    """
    text = text.strip()
    if not text:
        return []

    chunks = []
    start_index = 0
    while start_index < len(text):
        # Trim leading whitespace for the next chunk search
        while start_index < len(text) and text[start_index].isspace():
            start_index += 1
        if start_index >= len(text):
            break # Reached end of text just trimming spaces

        end_index = min(start_index + chunk_size, len(text))
        chunk_candidate = text[start_index:end_index]
        whitespace_matches = None # Initialize whitespace_matches
        whitespace_len = 0 # Initialize whitespace_len

        # If the remaining text is within chunk_size, take it all - MOVED LATER
        # if len(text) - start_index <= chunk_size:
        #    chunks.append(text[start_index:])
        #    break

        split_pos = -1
        found_split_point = False # Flag to track if we found a sentence/whitespace split

        # 1. Try to find the last sentence ending within the chunk candidate
        # Search backwards from the end of the candidate
        sentence_matches = list(SENTENCE_ENDINGS.finditer(chunk_candidate))
        if sentence_matches:
            # Find the match closest to the end of the chunk_candidate
            last_match = sentence_matches[-1]
            # Split *after* the punctuation and any following space
            split_pos = last_match.end()
            found_split_point = True

        # 2. If no sentence ending found, try to find the last whitespace
        if split_pos == -1:
            whitespace_matches = list(WHITESPACE.finditer(chunk_candidate))
            if whitespace_matches:
                # Find the match closest to the end
                last_match = whitespace_matches[-1]
                # Split *at* the start of the whitespace
                split_pos = last_match.start()
                # Store the length of the whitespace found to skip it later
                whitespace_len = last_match.end() - last_match.start()
                found_split_point = True
            # else: # No whitespace found either, keep whitespace_len = 0
            #     whitespace_len = 0

        # 3. If neither found, or split_pos is at the very beginning (e.g., leading space matched)
        #    force split at chunk_size if the candidate is full length.
        #    If the candidate is shorter (end of text), split_pos remains -1, handled below.
        # -- Removed forced split --
        # if split_pos <= 0 and end_index == start_index + chunk_size:
        #      split_pos = chunk_size # Force split at the boundary

        # Determine the actual end of the chunk
        if split_pos > 0:
            # Split point found (sentence or whitespace)
            actual_end_index = start_index + split_pos
        else:
            # No split point found, take the whole candidate up to chunk_size or end of text
            actual_end_index = end_index
            # -- Removed complex check --
            # If no split point found OR remaining text is <= chunk_size and we DIDN'T find a split point
            # if not found_split_point and len(text) - start_index <= chunk_size:
            #      # Take the whole remainder ONLY if no split point was identified
            #      actual_end_index = len(text)
            # else:
            #     # Force split at chunk_size if no other split found, or handle end of text
            #     actual_end_index = end_index
            # whitespace_len = 0 # No whitespace split occurred # Already initialized

        final_chunk = text[start_index:actual_end_index].strip()
        if final_chunk: # Avoid adding empty chunks from stripping
             chunks.append(final_chunk)

        # Move start_index for the next iteration
        # We already handle trimming leading whitespace at the start of the loop
        start_index = actual_end_index
        # No, we need to skip the whitespace that *caused* the split if it was a whitespace split
        # Let's revert the complex logic and simplify. Strip handles trailing/leading spaces of the *chunk*.
        # The primary loop advance should just be to the end of the identified chunk.
        # We will add explicit skipping of leading whitespace at the *start* of the loop.

    # Filter out potentially empty strings that might arise from splitting/stripping
    return [chunk for chunk in chunks if chunk]

# Example usage (optional, for testing)
# if __name__ == '__main__':
#     logging.basicConfig(level=logging.DEBUG)
#     sample_text = "First sentence. Second sentence! Third sentence? 中文句点。下一句！再来一句？This is a long string without proper sentence endings just spaces. LongStringWithoutAnySpacesOrPunctuationAtAll.  End.  "
#     chunk_sz = 30
#     split_chunks = split_text_intelligently(sample_text, chunk_sz)
#     print(f"--- Splitting with chunk size {chunk_sz} ---")
#     for i, chunk in enumerate(split_chunks):
#         print(f"Chunk {i+1} (Length: {len(chunk)}):\n'{chunk}'\n")

#     chinese_no_punc = "这是一段没有标点符号的中文长文本用于测试"
#     split_chunks = split_text_intelligently(chinese_no_punc, 10)
#     print(f"--- Splitting Chinese no punc with chunk size 10 ---")
#     for i, chunk in enumerate(split_chunks):
#         print(f"Chunk {i+1} (Length: {len(chunk)}):\n'{chunk}'\n")

#     long_word = "LongStringWithoutAnySpacesOrPunctuationAtAll"
#     split_chunks = split_text_intelligently(long_word, 15)
#     print(f"--- Splitting long word with chunk size 15 ---")
#     for i, chunk in enumerate(split_chunks):
#         print(f"Chunk {i+1} (Length: {len(chunk)}):\n'{chunk}'\n")
