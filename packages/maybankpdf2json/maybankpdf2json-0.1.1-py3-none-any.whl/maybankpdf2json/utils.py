from datetime import datetime
from typing import TypedDict
import numpy as np
import pdfplumber

START_ENTRY = "BEGINNING BALANCE"
END_ENTRY = "TOTAL DEBIT"
NOTE_START_ENTRY = "Perhation / Note"
NOTE_END_ENTRY = (
    "ENTRY DATE TRANSACTION DESCRIPTION TRANSACTION AMOUNT STATEMENT BALANCE"
)
EXCLUDE_ITEMS = ["TOTAL CREDIT", "TOTAL DEBIT", "ENDING BALANCE"]

Output = TypedDict("Output", {"date": str, "desc": str, "bal": float, "trans": float})


def parse_acc_value(value: str) -> float:
    value = value.replace(",", "")
    if value.endswith("-"):
        return -float(value[:-1])
    elif value.endswith("+"):
        return float(value[:-1])
    else:
        return float(value)


def is_valid_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%d/%m/%y")
        return True
    except ValueError:
        return False


def get_mapped_data(arr):
    narr = []

    i = 0
    while i < len(arr):
        current = arr[i]
        splitted = current.split()
        obj: Output = {"desc": "", "bal": 0, "trans": 0, "date": ""}

        if i != 0 and (not (is_valid_date(splitted[0]))):
            i += 1
            continue
        elif i == 0:
            obj["desc"] = " ".join(splitted[0:2])
            obj["bal"] = parse_acc_value(splitted[2])
            narr.append(obj)
        elif is_valid_date(splitted[0]):
            obj["date"] = splitted[0]
            obj["trans"] = parse_acc_value(splitted[-2])
            obj["bal"] = parse_acc_value(splitted[-1])
            obj["desc"] = " ".join(splitted[1:-2])

            i += 1
            while i < len(arr) and not is_valid_date(arr[i].split()[0]):
                obj["desc"] = obj["desc"] + " " + " ".join(arr[i].split())
                i += 1
            narr.append(obj)
            continue
        i += 1

    narr[0]["date"] = datetime.strptime(narr[2]["date"], "%d/%m/%y").strftime(
        "01/%m/%y"
    )

    return narr


def expand_ranges(arr: list[int]):
    expanded = []

    for ar in range(0, len(arr), 2):
        f = arr[ar]
        s = arr[ar + 1]
        for i in range(f, s + 1):
            expanded.append(i)

    return expanded


def get_filtered_data(arr):
    indexes = [0, len(arr)]

    for i, x in enumerate(arr):
        if x.startswith(START_ENTRY):
            indexes[0] = i
        elif x.startswith(END_ENTRY):
            indexes[1] = i + 1
            break

    filtered = arr[indexes[0] : indexes[1]]

    temp = np.array(filtered)
    notes_indices = np.where(
        np.char.startswith(temp, NOTE_START_ENTRY)
        | np.char.startswith(temp, NOTE_END_ENTRY)
    )[0].tolist()

    expanded = expand_ranges(notes_indices)

    narr = []

    for i, v in enumerate(temp):
        if i not in expanded and (
            not any(v.startswith(item) for item in EXCLUDE_ITEMS)
        ):
            narr.append(v)

    return narr


def read(s):
    with pdfplumber.open(s.buffers, password=s.pwd) as pdf:
        return [
            txt
            for pg, page in enumerate(pdf.pages)
            for txt in page.extract_text().split("\n")
        ]


def convert_to_json(s):
    r = read(s)
    d = get_filtered_data(r)
    return get_mapped_data(d)
