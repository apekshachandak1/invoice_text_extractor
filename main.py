import streamlit as st
import cv2
import json
import re
import easyocr
import numpy as np
from PIL import Image

# ----------------- STREAMLIT CONFIG -----------------
st.set_page_config(
    page_title="Invoice Text Extractor",
    layout="centered"
)

st.title("🧾 Invoice Text Extractor")
st.write("Upload an invoice image to extract structured data")

# ----------------- OCR INIT -----------------
@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

# ----------------- IMAGE PREPROCESS -----------------
def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    processed = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 2
    )
    return processed

# ----------------- INVOICE EXTRACTION -----------------
def extract_invoice_data(img):
    processed = preprocess_image(img)

    ocr_result = reader.readtext(processed)
    lines = [res[1].strip() for res in ocr_result if res[1].strip()]

    invoice_data = {
        "Invoice Number": "Not Found",
        "Invoice Date": "Not Found",
        "Line Items": []
    }

    # Invoice Number
    for line in lines:
        if "invoice" in line.lower() and any(c.isdigit() for c in line):
            digits = ''.join(filter(str.isdigit, line))
            if len(digits) >= 6:
                invoice_data["Invoice Number"] = digits
                break

    # Invoice Date
    date_patterns = [
        r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
        r"\d{4}[/-]\d{1,2}[/-]\d{1,2}"
    ]

    for line in lines:
        for pattern in date_patterns:
            match = re.search(pattern, line)
            if match:
                invoice_data["Invoice Date"] = match.group(0)
                break
        if invoice_data["Invoice Date"] != "Not Found":
            break

    # Group line items
    structured_items = []
    item_block = ""

    for line in lines:
        if re.match(r"^\d{1,2}[\.\)]?\s", line):
            if item_block:
                structured_items.append(item_block.strip())
            item_block = line
        else:
            item_block += " " + line

    if item_block:
        structured_items.append(item_block.strip())

    # Parse line items
    parsed_items = []

    for item in structured_items:
        parsed = {
            "Description": "",
            "Qty": None,
            "Unit": "",
            "Net price": None,
            "Net worth": None,
            "VAT": None,
            "Gross worth": None
        }

        # Quantity
        qty_match = re.search(r"(\d{1,4}[.,]?\d*)\s*(each|pcs|box|unit|pack)?", item, re.I)
        if qty_match:
            try:
                parsed["Qty"] = float(qty_match.group(1).replace(",", "."))
                parsed["Unit"] = qty_match.group(2) or "each"
            except:
                pass

        # Prices
        prices = re.findall(r"(\d{1,5}[.,]\d{2})", item)
        prices = [float(p.replace(",", ".")) for p in prices]

        if len(prices) >= 4:
            parsed["Net price"], parsed["Net worth"], parsed["VAT"], parsed["Gross worth"] = prices[:4]
        elif len(prices) == 3:
            parsed["Net price"], parsed["Net worth"], parsed["Gross worth"] = prices
        elif len(prices) == 2:
            parsed["Net worth"], parsed["Gross worth"] = prices

        # Description
        desc = re.sub(r"(\d{1,5}[.,]\d{2})", "", item)
        desc = re.sub(r"^\d{1,2}[\.\)]?\s*", "", desc)
        parsed["Description"] = desc.strip()

        parsed_items.append(parsed)

    invoice_data["Line Items"] = parsed_items
    return invoice_data, lines

# ----------------- STREAMLIT UI -----------------
uploaded_file = st.file_uploader(
    "Upload Invoice Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    image = Image.open(uploaded_file)
    img_array = np.array(image)

    st.image(image, caption="Uploaded Invoice", use_column_width=True)

    with st.spinner("Extracting invoice data..."):
        invoice_data, raw_lines = extract_invoice_data(img_array)

    st.subheader("📄 Extracted Text")
    st.text_area("", "\n".join(raw_lines), height=200)

    st.subheader("📦 Structured Invoice Data")
    st.json(invoice_data)

    st.download_button(
        "⬇️ Download JSON",
        data=json.dumps(invoice_data, indent=4),
        file_name="invoice_data.json",
        mime="application/json"
    )
