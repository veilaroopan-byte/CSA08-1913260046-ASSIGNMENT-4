from decimal import Decimal, InvalidOperation
from pathlib import Path

def process_mess_file(filename):
    total = Decimal("0.00")
    report_rows = []
    rejected = []

    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line_number, raw_line in enumerate(file, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                parts = [part.strip() for part in line.split(",")]
                if len(parts) != 3:
                    rejected.append((line_number, raw_line.rstrip("\n"), "expected 3 fields"))
                    continue
                register_no, name, amount_text = parts
                try:
                    amount = Decimal(amount_text)
                except InvalidOperation:
                    rejected.append((line_number, raw_line.rstrip("\n"), "amount is not numeric"))
                    continue
                if not amount.is_finite() or amount < 0:
                    rejected.append((line_number, raw_line.rstrip("\n"), "amount must be finite and non-negative"))
                    continue
                total += amount
                report_rows.append(f"{name} {amount:.2f}")
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as exc:
        raise RuntimeError(f"Could not process {filename}: {exc}") from exc

    return "\n".join(report_rows), total, rejected

if __name__ == "__main__":
    report, total, rejected = process_mess_file("mess_oct.txt")
    print(report)
    print(f"Total {total:.2f}")
    print("Rejected:", rejected)
