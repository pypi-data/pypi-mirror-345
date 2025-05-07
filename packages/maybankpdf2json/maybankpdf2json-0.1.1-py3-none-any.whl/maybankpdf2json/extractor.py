from typing import List, Union, BinaryIO
from .utils import convert_to_json


class MaybankPdf2Json:
    def __init__(self, buffers: Union[List[BinaryIO], BinaryIO], pwd: str):
        if isinstance(buffers, list):
            self.buffers = buffers
        else:
            self.buffers = [buffers]
        self.pwd = pwd

    def json(self):
        return convert_to_json(self)
