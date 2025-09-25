import os
import csv
import re

# --- CONFIG ---
folder_of_books = 'books'
folder_of_movies = 'movies-tv'
output_folder = 'output'
os.makedirs(output_folder, exist_ok=True)

CHUNK_SIZE = 1020  # number of words per chunk
STRIDE = 256       # overlap in words

def split_into_chunks(text, chunk_size=CHUNK_SIZE, stride=STRIDE):
    words = text.split()
    chunks = []
    step = chunk_size - stride
    for start in range(0, len(words), step):
        chunk_words = words[start:start + chunk_size]
        if chunk_words:
            chunks.append(' '.join(chunk_words))
        if start + chunk_size >= len(words):
            break
    return chunks

def create_csv_chunked_local(folder_path, output_filename):
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
                    # clean text
                    content_no_tabs = content.replace('\t', ' ')
                    content_cleaned = re.sub(r' {2,}', ' ', content_no_tabs).strip()

                    # split into chunks
                    chunks = split_into_chunks(content_cleaned, CHUNK_SIZE, STRIDE)
                    for chunk in chunks:
                        csv_writer.writerow([title, chunk])

            except UnicodeDecodeError:
                print(f"Skipping {filename} due to a UnicodeDecodeError. Check encoding.")
            except Exception as e:
                print(f"Error with file {filename}: {e}")

    print(f"Successfully created '{output_filename}' with chunked data.")

create_csv_chunked_local(folder_of_books, f"{folder_of_books}.csv")
create_csv_chunked_local(folder_of_movies, f"{folder_of_movies}.csv")