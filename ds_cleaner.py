import os
import csv
import re

def create_csv(folder_path, output_filename):
    """
    Creates a CSV file with book titles and content from a folder of TXT files.
    The content is wrapped in <BOS> and <EOS> tags, and filenames are formatted as titles.

    Args:
        folder_path (str): The path to the folder containing the TXT files.
        output_filename (str): The name of the output CSV file.
    """
    output_path = os.path.join(os.getcwd(), output_filename)

    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        csv_writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['title', 'content'])

        for filename in os.listdir(folder_path):
            if filename.endswith(".txt"):
                file_path = os.path.join(folder_path, filename)

                # Format the title: replace hyphens with spaces and capitalize each word
                title = os.path.splitext(filename)[0].replace('-', ' ').title()

                try:
                    with open(file_path, 'r', encoding='utf-8') as txtfile:
                        content = txtfile.read()

                        # Remove extra spaces (more than one in a row) from the content
                        content_cleaned = re.sub(r' {2,}', ' ', content)

                        # Wrap content with <BOS> and <EOS> tags
                        content_wrapped = f"<|im_start|>{content_cleaned}<|im_end|>"

                        # Replace newlines with the escaped character `\n`
                        content_escaped = content_wrapped.replace('\n', '\\n')

                        # Add <TITLE> tag to the title
                        title_formatted = f"<|im_start|>{title}<|im_end|>"

                        # Write the row to the CSV file
                        csv_writer.writerow([title_formatted, content_escaped])

                except UnicodeDecodeError:
                    print(f"Skipping {filename} due to a UnicodeDecodeError. Please check the file's encoding.")
                except Exception as e:
                    print(f"An error occurred with file {filename}: {e}")

    print(f"Successfully created '{output_filename}' with book data.")

# --- Usage Example ---
folder_of_books = 'books'
folder_of_movies = 'movies-tv'
create_csv(folder_of_books, f"output/{folder_of_books}.csv")
create_csv(folder_of_movies, f"output/{folder_of_movies}.csv")