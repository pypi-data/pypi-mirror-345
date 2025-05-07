# Maybank PDF Account Statement to JSON

This package provides functionality to extract and process data from Maybank account statement PDFs. It allows users to read PDF files and extract json data from them.

## Installation

To install the package, clone the repository and run the following command:

```
pip install maybankpdf2json
```

## Usage

Here is a basic example of how to use the package:

```python
from maybankpdf2json import MaybankPdf2Json

# Initialize the MaybankPdf2Json object
mbb = MaybankPdf2Json(buffer, "01Jan2025")
data = mbb.json()

print(mapped_data)
[
  {
    "date": "01/01/2024",
    "desc": "Deposit from client",
    "trans": 50.0,
    "bal": 1050.0
  },
  {
    "date": "02/01/2024",
    "desc": "Purchase - Office Supplies",
    "trans": -20.0,
    "bal": 1030.0
  }
]
```

## Testing

To run the tests, navigate to the project directory and execute:

```
pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
