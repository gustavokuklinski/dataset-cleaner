import os
import csv
import re

# --- CONFIG ---
folder_of_books = 'books'
output_folder = 'output'
os.makedirs(output_folder, exist_ok=True)

# Define the separator for chunking
CHUNK_SEPARATOR = '\n\n' # Double newline often signifies a paragraph break

def split_into_newline_chunks(text, separator=CHUNK_SEPARATOR):
    """
    Splits text into chunks based on a newline separator (e.g., paragraph breaks).
    Empty or whitespace-only chunks are ignored.
    """
    # Split the text by the defined separator
    chunks = text.split(separator)
    
    # Filter out chunks that are empty or only contain whitespace
    cleaned_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    
    return cleaned_chunks

def create_csv(folder_path, output_filename):
    output_path = os.path.join(output_folder, output_filename)

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['title', 'text'])

        for filename in os.listdir(folder_path):
            if not filename.endswith(".txt"):
                continue

            file_path = os.path.join(folder_path, filename)
            title = os.path.splitext(filename)[0].replace('-', ' ').title()

            try:
                with open(file_path, 'r', encoding='utf-8') as txtfile:
                    content = txtfile.read()
                    
                    # 1. Standardize line endings and clean tabs
                    content_standardized = content.replace('\r\n', '\n').replace('\r', '\n').replace('\t', ' ')
                    
                    # 2. ***NEW CRUCIAL STEP: Merge Soft Line Wraps***
                    # Replace single newlines (which appear WITHIN a paragraph/sentence) 
                    # with a single space. This restores the sentence continuity.
                    # We use a negative lookahead/lookbehind to target single '\n's, 
                    # preserving the double '\n\n' used for paragraph breaks.
                    content_merged = re.sub(r'(?<!\n)\n(?!\n)', ' ', content_standardized)
                    
                    # 3. Handle multiple newlines: Reduce sequences of 3 or more newlines
                    # to a maximum of two newlines (CHUNK_SEPARATOR), preserving paragraph breaks.
                    content_reduced_newlines = re.sub(r'\n\n+', '\n\n', content_merged)
                    
                    # 4. Reduce multiple spaces to a single space and strip leading/trailing
                    content_final = re.sub(r' {2,}', ' ', content_reduced_newlines).strip()

                    # Split into chunks based on the double newline
                    chunks = split_into_newline_chunks(content_final, CHUNK_SEPARATOR)
                    
                    for chunk in chunks:
                        csv_writer.writerow([title, chunk])

            except UnicodeDecodeError:
                print(f"Skipping {filename} due to a UnicodeDecodeError. Check encoding.")
            except Exception as e:
                print(f"Error with file {filename}: {e}")

    print(f"Successfully created '{output_filename}' chunked data.")

# --- Execution ---
create_csv(folder_of_books, "books.csv")