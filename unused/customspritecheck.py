import csv
import re
import requests

def process_csv(input_file, output_file, exclude_keywords):
    # Regular expression to check for non-numeric characters
    non_numeric = re.compile(r'[^\d.]+')

    # Open input and output CSV files
    with open(input_file, 'r', encoding='utf-8-sig') as f_input, open(output_file, 'w', newline='', encoding='utf-8') as f_output:
        csv_reader = csv.reader(f_input)
        csv_writer = csv.writer(f_output)

        for row in csv_reader:
            if (len(row) >= 3 and not any(keyword in row[2] for keyword in exclude_keywords) and
                non_numeric.search(row[0]) is None and
                '.' in row[0]):
                if not all(cell == '' for cell in row):
                    # Write columns 1 and 3 from CSV to TXT file, each on the same line
                    f_output.write(f"{row[0]}.{row[2]}\n")

def download_file(url, local_filename):
    # Send a GET request to the URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses

    # Write the content to a local file
    with open(local_filename, 'wb') as f:
        f.write(response.content)

def main():
    url = 'https://gitlab.com/pokemoninfinitefusion/customsprites/-/raw/master/Sprite%20Credits.csv'
    local_csv_filename = 'Sprite Credits.csv'
    
    # Download the CSV file
    download_file(url, local_csv_filename)
    
    # Define the filtering criteria and corresponding output files
    criteria = [
        (['alt', 'temp'], 'mainSprites.txt'),
        (['alt', 'main'], 'tempSprites.txt'),
        (['temp', 'main'], 'altSprites.txt')
    ]
    
    # Process the CSV for each criteria
    for exclude_keywords, output_file in criteria:
        process_csv(local_csv_filename, output_file, exclude_keywords)
        print(f"Processed CSV saved to {output_file}")

if __name__ == "__main__":
    main()