import chardet

input_csv_file = "FIFA World Cup All Goals 1930-2022.csv"

with open(input_csv_file, 'rb') as input_file:
    detector = chardet.universaldetector.UniversalDetector()
    for line in input_file:
        detector.feed(line)
        if detector.done:
            break
    detector.close()

detected_encoding = detector.result['encoding']

print(f"Detected encoding: {detected_encoding}")