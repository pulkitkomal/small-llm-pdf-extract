import fitz

doc = fitz.open()

# Page 1: Mixed text + table
page = doc.new_page()
page.insert_text((50, 50), "Invoice", fontsize=24)
page.insert_text((50, 100), "Date: 2024-06-01", fontsize=12)
page.insert_text((50, 130), "Customer: ACME Corp", fontsize=12)
y = 180
for row_i, row in enumerate([
    ["Item", "Qty", "Price"],
    ["Widget A", "2", "$20"],
    ["Widget B", "1", "$15"],
    ["Total", "", "$35"],
]):
    for col_i, cell in enumerate(row):
        page.insert_text((50 + col_i * 120, y + row_i * 30), cell, fontsize=11)

# Page 2: Text content
page = doc.new_page()
page.insert_text((50, 50), "Terms & Conditions", fontsize=18)
page.insert_text(
    (50, 100),
    "Payment is due within 30 days. Late payments incur a 5% fee.",
    fontsize=11,
)

# Page 3: Blank
doc.new_page()

import os
out = os.path.join(os.path.dirname(__file__), "sample_invoice.pdf")
doc.save(out)
doc.close()
print("Created pdfs/sample_invoice.pdf")
