import csv
import re

def process_csv(input_file, output_file):
    # Regular expression to check for non-numeric characters
    non_numeric = re.compile(r'[^\d.]+')

    # Open input and output CSV files
    with open(input_file, 'r', encoding='utf-8-sig') as f_input, open(output_file, 'w', newline='', encoding='utf-8') as f_output:
        csv_reader = csv.reader(f_input)
        csv_writer = csv.writer(f_output)

        for row in csv_reader:
            if (len(row) >= 3 and "alt" not in row[2] and           # Task 2
                non_numeric.search(row[0]) is None and              # Task 3
                '.' in row[0]):                                     # Task 4
                if not all(cell == '' for cell in row):             # Task 5
                    csv_writer.writerow([row[0]])                   # Write only the first column to output file

def main():
    input_file = 'Sprite Credits.csv'    # Replace with your input CSV file
    output_file = 'customSprites.txt'    # Replace with your desired output CSV file

    process_csv(input_file, output_file)
    print(f"Processed CSV saved to {output_file}")

if __name__ == "__main__":
    main()