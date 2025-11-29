import os
from pypdf import PdfReader

pdf_path = 'tcs_part_A_lectue_01.pdf'
output_path = 'lecture_01_content.txt'

if not os.path.exists(pdf_path):
    print(f"Error: {pdf_path} not found.")
    exit(1)

reader = PdfReader(pdf_path)
with open(output_path, 'w', encoding='utf-8') as f:
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        f.write(f"--- PAGE {i+1} ---\n")
        f.write(text)
        f.write("\n\n")

print(f"Extracted {len(reader.pages)} pages to {output_path}")
