import os
import csv
import re

# --- CONFIG ---
folder_of_books = 'books'
output_folder = 'output'
os.makedirs(output_folder, exist_ok=True)

# Define the target maximum chunk size in characters
# Note: The actual chunk size may be smaller to respect sentence boundaries.
MAX_CHUNK_SIZE = 2048 
# Define the minimum size a chunk can be before trying to merge it with the next one
# This helps prevent very tiny leftover chunks.
MIN_CHUNK_SIZE = 50 

def split_into_size_chunks(text, max_size=MAX_CHUNK_SIZE, min_size=MIN_CHUNK_SIZE):
    """
    Splits text into chunks of approximately max_size characters,
    prioritizing splitting at sentence ends ('.', '!', '?').
    """
    chunks = []
    current_position = 0
    text_length = len(text)
    
    # Define sentence-ending punctuation pattern for lookahead
    sentence_end_pattern = r'[.!?]'

    while current_position < text_length:
        # 1. Determine the end of the current chunk
        
        # Start looking from the target maximum size
        end_search_start = min(current_position + max_size, text_length)
        
        # If we're near the end of the text and the remaining text is small,
        # just take the rest as a final chunk.
        remaining_length = text_length - current_position
        if remaining_length <= max_size:
            chunk_end = text_length
        else:
            # 2. Search backward from the max_size boundary for a sentence end
            
            # Slice the potential chunk (up to max_size) for searching
            search_area = text[current_position : end_search_start]
            
            # Find the last sentence end (., !, ?) that occurs before the max_size limit
            # We look for a pattern followed by zero or more whitespace/quotes
            
            # The regex finds the last match of a sentence end in the search area.
            match = None
            # Iterate backwards to find the best split point
            for i in range(len(search_area) - 1, max_size // 2, -1):
                if re.match(sentence_end_pattern, search_area[i]):
                    # Check if the next character is not part of an abbreviation (e.g., 'Mr.')
                    # This check is basic; full NLP is complex. We simply ensure the next char
                    # is a space or newline, which is typical of a sentence break.
                    if (i + 1 < len(search_area)) and (search_area[i+1] in (' ', '\n')):
                        match = i + 1  # Split *after* the punctuation and space
                        break
            
            if match is not None:
                # Found a good sentence break point
                chunk_end = current_position + match
            else:
                # No good sentence break found within the target size range, 
                # or the remaining text is too long.
                # Just split at the maximum size limit to prevent oversized chunks.
                chunk_end = end_search_start
        
        # Extract the chunk
        chunk = text[current_position:chunk_end].strip()
        
        if chunk:
            # Check for very small trailing chunks and merge them if possible
            if (len(chunks) > 0) and (len(chunk) < min_size) and (len(chunks[-1]) + len(chunk) < max_size):
                # Merge the small chunk into the previous one
                chunks[-1] += ' ' + chunk
            else:
                chunks.append(chunk)

        current_position = chunk_end
        
        # Skip any leading whitespace/newlines for the next iteration
        while current_position < text_length and text[current_position].isspace():
            current_position += 1

    # Final cleanup: If the last chunk is very small, try to merge it
    if len(chunks) > 1 and len(chunks[-1]) < min_size and len(chunks[-2]) + len(chunks[-1]) + 1 <= max_size:
        last_chunk = chunks.pop()
        chunks[-1] += ' ' + last_chunk
        
    return chunks

def create_csv(folder_path, output_filename):
    output_path = os.path.join(output_folder, output_filename)

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['text'])

        for filename in os.listdir(folder_path):
            if not filename.endswith(".txt"):
                continue

            file_path = os.path.join(folder_path, filename)
            # title = os.path.splitext(filename)[0].replace('-', ' ').title() # Title is not used in the chunking, so it's commented out

            try:
                with open(file_path, 'r', encoding='utf-8') as txtfile:
                    content = txtfile.read()
                    
                    # 1. Standardize line endings and clean tabs
                    content_standardized = content.replace('\r\n', '\n').replace('\r', '\n').replace('\t', ' ')
                    
                    # 2. ***CRUCIAL STEP: Merge Soft Line Wraps***
                    # Replace single newlines (which appear WITHIN a paragraph/sentence) 
                    # with a single space.
                    # We use a negative lookahead/lookbehind to target single '\n's.
                    content_merged = re.sub(r'(?<!\n)\n(?!\n)', ' ', content_standardized)
                    
                    # 3. Handle multiple newlines: Reduce sequences of 2 or more newlines
                    # to a single space. Since we are chunking by size, we just want a single,
                    # continuous block of text without artificial paragraph breaks, 
                    # as sentence breaks will be handled by the new chunker.
                    content_single_space = re.sub(r'\n{2,}', ' ', content_merged)
                    
                    # 4. Reduce multiple spaces to a single space and strip leading/trailing
                    content_final = re.sub(r' {2,}', ' ', content_single_space).strip()

                    # 🔑 Split into chunks based on character size, respecting sentence boundaries
                    chunks = split_into_size_chunks(content_final)
                    
                    for chunk in chunks:
                        csv_writer.writerow([chunk])

            except UnicodeDecodeError:
                print(f"Skipping {filename} due to a **UnicodeDecodeError**. Check encoding.")
            except Exception as e:
                print(f"Error with file {filename}: {e}")

    print(f"Successfully created '{output_filename}' character-chunked data.")

# --- Execution ---
create_csv(folder_of_books, "books_2048_char_chunks.csv")