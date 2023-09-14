import csv
import chardet

# Archivo CSV original
input_csv_file = "FIFA World Cup All Goals 1930-2022.csv"

# Archivo CSV corregido
output_csv_file = "FIFA World Cup All Goals 1930-2022_corregido.csv"

with open(input_csv_file, 'r', encoding='utf-8') as input_file, open(output_csv_file, 'w', newline='', encoding='utf-8') as output_file:
    csv_reader = csv.reader(input_file)
    csv_writer = csv.writer(output_file)

    for row in csv_reader:
        corrected_row = [field.replace(',', '\\,') if ',' in field else field for field in row]

        csv_writer.writerow(corrected_row)

print("Archivo CSV corregido creado con éxito.")
