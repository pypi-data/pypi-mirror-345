import unittest
from maybank_acc_extractor.extractor import read_pdfs, get_filtered_data, get_mapped_data

class TestExtractor(unittest.TestCase):

    def setUp(self):
        self.test_pdf_path = "path/to/test/pdf"  # Update with actual test PDF path
        self.test_password = "test_password"  # Update with actual test password
        self.test_data = [
            "BEGINNING BALANCE 1000.00",
            "01/01/22 Transaction Description 100.00 1100.00",
            "02/01/22 Transaction Description -50.00 1050.00",
            "TOTAL DEBIT 50.00"
        ]

    def test_read_pdfs(self):
        pdf_data = read_pdfs(self.test_pdf_path, self.test_password)
        self.assertIsInstance(pdf_data, list)

    def test_get_filtered_data(self):
        filtered_data = get_filtered_data(self.test_data)
        self.assertGreater(len(filtered_data), 0)

    def test_get_mapped_data(self):
        filtered_data = get_filtered_data(self.test_data)
        mapped_data = get_mapped_data(filtered_data)
        self.assertIsInstance(mapped_data, list)
        self.assertGreater(len(mapped_data), 0)
        self.assertIn("date", mapped_data[0])
        self.assertIn("desc", mapped_data[0])
        self.assertIn("trans", mapped_data[0])
        self.assertIn("bal", mapped_data[0])

if __name__ == "__main__":
    unittest.main()