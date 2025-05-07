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


def output_extracted_data(value, options):
    type = options["format"]
    is_json = type == "json"
    newline = None if is_json else ""
    date = datetime.strptime(value[2]["date"], "%d/%m/%y")
    file_date = date.strftime("%Y%m %B ") if not options["merge"] else "-COMBINED"

    with open(f"{OUTPUT_FILENAME}{file_date}.{type}", "w", newline=newline) as o_file:
        if is_json:
            json.dump(value, o_file, indent=4)
        else:
            writer = csv.DictWriter(o_file, ["date", "desc", "trans", "bal"])
            writer.writeheader()
            writer.writerows(value)