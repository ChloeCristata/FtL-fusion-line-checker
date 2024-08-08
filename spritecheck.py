# This code...

# 1. Downloads 'Sprite Credits.csv' from the Pokemon Infinite Fusion gitlab
# 2. Processes the information from the CSV file
# 3. Outputs a TXT file which lists the sprite ID and whether the sprite is a main, temp, or alt

# The resulting TXT file is used by gen.py when generating and exporting CSV files to be used by the Google Sheets auto-chart.

import csv
import re
import requests

def process_csv(input_file, output_file):
    # Regular expression to check for non-numeric characters
    non_numeric = re.compile(r'[^\d.]+')

    # Open input and output CSV files
    with open(input_file, 'r', encoding='utf-8-sig') as f_input, open(output_file, 'w', newline='', encoding='utf-8') as f_output:
        csv_reader = csv.reader(f_input)

        for row in csv_reader:
            if len(row) >= 3 and \
               non_numeric.search(row[0]) is None and \
               row[0].count('.') == 1:  # Check for exactly one period
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
    
    input_file = 'Sprite Credits.csv'
    output_file = 'spritestatuses.txt'

    process_csv(input_file, output_file)
    print(f"Processed CSV saved to {output_file}")

if __name__ == "__main__":
    main()
