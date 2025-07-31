
# Invoice OCR Parser

A Python-based tool using Tesseract OCR to extract structured data (like invoice number, seller info, items, and totals) from invoice images and export them to JSON format.

## What is an Invoice?

An **invoice** is a document issued by a seller to a buyer, listing the products or services provided, their prices, and the total amount due.

### Common Invoice Elements:
- **Invoice Number**: Unique ID for each invoice
- **Invoice Date**: Date the invoice was created
- **Seller Details**: Company name, address, contact info, Tax ID
- **Client Details**: Buyer info such as name and address
- **Line Items**: List of purchased items (description, quantity, price, etc.)
- **Summary**: Net worth, VAT, and Gross worth totals

---
## Features

Extracts key fields from invoices:
- Invoice Number  
- Invoice Date  
- Seller and Buyer (Client) Details  
- Line Items (Product details, Quantity, Prices, Taxes)  
- Summary of total amounts

✅ Preprocesses image for better OCR results  
✅ Supports batch image processing  
✅ Saves results in structured **JSON** format  
✅ Modular and extendable design  

---

##  Technologies Used 
- Python – core scripting language  
- Tesseract OCR – text recognition engine  
- OpenCV – image preprocessing (grayscale, thresholding)  
- Regex – text filtering & structured parsing  
- JSON – output storage format  

---

## Project Structure

```

invoice-text-parser/
├── data/
│   └── batch\_1/               # Place your invoice images here
├── outputs/                   # Output JSON files will be stored here
├── main.py                    # Main OCR and parsing script
├── requirements.txt           # Python dependencies
├── README.md                  # This documentation

````

---

## 🔄 Workflow

1. **Image Input**  
   Put your invoices in `data/batch_1/`.

2. **Preprocessing**  
   Enhances contrast, binarizes the image, and corrects skew using OpenCV.

3. **Text Extraction**  
   Uses **Tesseract OCR** to extract raw text from the image.

4. **Parsing**  
   Extracts structured fields using Regex and string pattern matching:
   - Invoice Number
   - Date
   - Seller/Client Information
   - Line Items (Qty, Unit, Description, Price, Tax, etc.)
   - Summary (Net Total, VAT, Gross Total)

5. **Output as JSON**  
   The extracted details are saved in `/outputs/` as structured `.json` files.

---

## 🧪 Sample Output

Example JSON output after running the script:

```json
{
  "Invoice Number": "12847181",
  "Invoice Date": "03/03/2012",
  "Seller": {
    "Name": "Fitzpatrick and Sons Duncan PLC",
    "Address": "00480 Cook Cove Unit 8799 Box 0703",
    "City_State_Zip": "Spencerport, UT 12036 DPO AP 81970",
    "Tax ID": "911-82-7132",
    "IBAN": "GB92PBPQ73499358975916"
  },
  "Client": {
    "Name": "",
    "Address": "",
    "City_State_Zip": "",
    "Tax ID": ""
  },
  "Line Items": [
    {
      "Description": "HP Desktop Computer PC",
      "Qty": 1.0,
      "Unit": "each",
      "Net price": 4.0,
      "Net worth": 139.95,
      "VAT": 559.8,
      "Gross worth": 615.78
    },
    {
      "Description": "CUSTOM BUILT AMD RYZEN",
      "Qty": 2.0,
      "Unit": "each",
      "Net price": 3.0,
      "Net worth": 400.0,
      "VAT": 200.0,
      "Gross worth": 620.0
    }
    // more items ...
  ],
  "Summary": {
    "Net worth": 780.0,
    "VAT": 858.0,
    "Gross worth": 5.25
  }
}
````

---

## ⚙️ Installation

### 1. Clone this repository:

```bash
git clone https://github.com/yourusername/invoice-text-parser.git
cd invoice-text-parser
```

### 2. Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

* Windows: Download from [here](https://github.com/tesseract-ocr/tesseract/wiki)
* Add the path to your system environment variable (e.g., `C:\Program Files\Tesseract-OCR\tesseract.exe`)

---

## ▶️ Run the Script

```bash
python main.py
```

It will read all images from `data/batch_1/` and save extracted data as JSON files in `outputs/`.

---

## 📦 Future Improvements

* GUI interface for invoice uploads
* Smart table detection using vision models
* PDF invoice support

---

## 📜 License

MIT License – feel free to use, modify, and distribute.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 🙌 Acknowledgements

* [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
* Python OpenCV, Regex
* Inspiration from real-world invoice automation tasks

```
