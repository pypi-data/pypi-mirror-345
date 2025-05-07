from typing import List, Dict, Union, BinaryIO
import pdfplumber

START_ENTRY = "BEGINNING BALANCE"
END_ENTRY = "TOTAL DEBIT"
EXCLUDE_ITEMS = ["TOTAL CREDIT", "TOTAL DEBIT", "ENDING BALANCE"]

class MaybankAccExtractor:
    def __init__(self, buffers: Union[List[BinaryIO], BinaryIO], pwd: str = None):
        if isinstance(buffers, list):
            self.buffers = buffers
        else:
            self.buffers = [buffers]
        self.pwd = pwd

    def read_pdfs(self) -> List[List[str]]:
        pdf_files = []
        for buffer in self.buffers:
            try:
                pdf_files.append(self.read_single_pdf_file(buffer, self.pwd))
            except Exception:
                pdf_files.append(self.read_single_pdf_file(buffer, None))
        return pdf_files

    def read_single_pdf_file(self, buffer: BinaryIO, pwd: str) -> List[str]:
        buffer.seek(0)
        with pdfplumber.open(buffer, password=pwd) as pdf:
            return [
                txt
                for page in pdf.pages
                for txt in page.extract_text().split("\n")
            ]

    def get_filtered_data(self, arr: List[str]) -> List[str]:
        indexes = [0, len(arr)]
        for i, x in enumerate(arr):
            if x.startswith(START_ENTRY):
                indexes[0] = i
            elif x.startswith(END_ENTRY):
                indexes[1] = i + 1
                break
        filtered = arr[indexes[0]: indexes[1]]
        narr = [v for v in filtered if not any(v.startswith(item) for item in EXCLUDE_ITEMS)]
        return narr

    def get_mapped_data(self, arr: List[str]) -> List[Dict[str, str]]:
        narr = []
        for current in arr:
            splitted = current.split()
            if len(splitted) < 3:
                continue
            obj = {
                "date": splitted[0],
                "desc": " ".join(splitted[1:-2]),
                "trans": float(splitted[-2]),
                "bal": float(splitted[-1])
            }
            narr.append(obj)
        return narr

    def extract_data(self) -> List[Dict[str, str]]:
        pdf_data = self.read_pdfs()
        all_mapped_data = []
        for pdf in pdf_data:
            filtered_data = self.get_filtered_data(pdf)
            mapped_data = self.get_mapped_data(filtered_data)
            all_mapped_data.extend(mapped_data)
        return all_mapped_data