# Maybank Account Statement Extractor

This package provides functionality to extract and process data from Maybank account statement PDFs. It allows users to read PDF files, filter relevant data, and map it into a structured format for further analysis or reporting.

## Features

- Extract data from PDF statements.
- Filter and map extracted data into a structured format.
- Utility functions for data manipulation and validation.

## Installation

To install the package, clone the repository and run the following command:

```
pip install .
```

## Usage

Here is a basic example of how to use the package:

```python
from maybank_acc_extractor.extractor import read_pdfs, get_filtered_data, get_mapped_data

# Read PDF files from a specified directory
pdf_data = read_pdfs('path/to/pdf/folder', 'your_password')

# Filter the data
filtered_data = get_filtered_data(pdf_data)

# Map the filtered data to a structured format
mapped_data = get_mapped_data(filtered_data)

# Output the mapped data
print(mapped_data)
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