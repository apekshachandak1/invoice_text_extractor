import os
import cv2
import pytesseract
import json
import re
import concurrent.futures
from datetime import datetime
from tqdm import tqdm

# 🔧 Update path to your tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 🧹 Preprocess image for better OCR
def preprocess_image(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 31, 2)
    return processed

# 🔍 Extract data from a single image
def extract_invoice_data(image_path):
    image = preprocess_image(image_path)
    if image is None:
        return None

    custom_config = r'--oem 3 --psm 6'
    text = pytesseract.image_to_string(image, config=custom_config)
    lines = [line.strip() for line in text.split("\n") if line.strip()]

    invoice_data = {
        "Invoice Number": "Not Found",
        "Invoice Date": "Not Found",
        "Line Items": []
    }

    # 🔢 Extract Invoice Number
    for line in lines:
        if "invoice" in line.lower() and any(char.isdigit() for char in line):
            digits = ''.join(filter(str.isdigit, line))
            if len(digits) >= 6:
                invoice_data["Invoice Number"] = digits
                break

    # 📅 Extract Invoice Date
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

    # 📦 Extract line item blocks
    structured_items = []
    item_block = ""
    for line in lines:
        if re.match(r"^\d{1,2}[\.\)]?\s", line):  # new item line starts
            if item_block:
                structured_items.append(item_block.strip())
            item_block = line
        else:
            item_block += " " + line
    if item_block:
        structured_items.append(item_block.strip())

    # 🧾 Parse line items
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

        # Extract Qty and Unit
        qty_unit_match = re.search(r"(\d{1,4},?\d*)\s*(each|pcs|box|unit|pack)?", item, re.IGNORECASE)
        if qty_unit_match:
            qty_text = qty_unit_match.group(1).replace(",", ".")
            try:
                parsed["Qty"] = float(qty_text)
            except:
                pass
            parsed["Unit"] = qty_unit_match.group(2) if qty_unit_match.group(2) else "each"

        # Extract Prices (handle , as decimal)
        prices = re.findall(r"(\d{1,5}[.,]\d{2})", item)
        prices = [float(p.replace(",", ".")) for p in prices]
        if len(prices) >= 4:
            parsed["Net price"] = prices[0]
            parsed["Net worth"] = prices[1]
            parsed["VAT"] = prices[2]
            parsed["Gross worth"] = prices[3]
        elif len(prices) >= 3:
            parsed["Net price"] = prices[0]
            parsed["Net worth"] = prices[1]
            parsed["Gross worth"] = prices[2]
        elif len(prices) == 2:
            parsed["Net worth"] = prices[0]
            parsed["Gross worth"] = prices[1]

        # Extract Description
        desc = re.sub(r"(\d{1,5}[.,]\d{2})", "", item)  # remove prices
        desc = re.sub(r"\d{1,2}[\.\)]?\s*", "", desc)   # remove item index
        parsed["Description"] = desc.strip()

        parsed_items.append(parsed)

    invoice_data["Line Items"] = parsed_items
    return invoice_data

# 💾 Save as JSON
def process_image(image_path, output_dir):
    try:
        data = extract_invoice_data(image_path)
        if data:
            file_name = os.path.basename(image_path).rsplit(".", 1)[0]
            output_path = os.path.join(output_dir, file_name + "_output.json")
            with open(output_path, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return f"✅ Saved: {output_path}"
    except Exception as e:
        return f"❌ Error: {image_path} -> {e}"
    return None

# 📂 Batch process a folder of images
def process_all_images(folder_path, output_dir="outputs", max_workers=8):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                image_files.append(os.path.join(root, file))

    print(f"🔍 Total images found: {len(image_files)}\n")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        for result in tqdm(executor.map(lambda img: process_image(img, output_dir), image_files), total=len(image_files)):
            if result:
                results.append(result)

    print("\n--- 📊 Processing Summary ---")
    for res in results:
        print(res)

# 🔁 Run main function
if __name__ == "__main__":
    folder_to_scan = "data/batch_1"  # ✅ Set your folder here
    process_all_images(folder_to_scan)
