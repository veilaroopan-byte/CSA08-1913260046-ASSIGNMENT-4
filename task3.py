import os
import tempfile

class InvalidRecord(Exception):
    """Raised when an attendance row is not in the required format."""

def parse_line(line):
    parts = line.strip().split(",")
    if len(parts) != 3:
        raise InvalidRecord(f"expected 3 fields, found {len(parts)}")
    register_no, date, status = (part.strip() for part in parts)
    if status not in {"P", "A"}:
        raise InvalidRecord(f"invalid status {status!r}")
    if not register_no or not date:
        raise InvalidRecord("register number and date must not be empty")
    return register_no, date, status

def summarise(path):
    present, absent, errors = 0, 0, []
    try:
        with open(path, "r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                try:
                    _, _, status = parse_line(line)
                except InvalidRecord as exc:
                    errors.append((line_number, str(exc)))
                    continue
                if status == "P":
                    present += 1
                else:
                    absent += 1
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as exc:
        raise RuntimeError(f"Unable to read attendance file {path}") from exc
    else:
        return present, absent, errors
    finally:
        # This block runs whether processing succeeds or fails.
        pass

if __name__ == "__main__":
    data = ("192311001,2026-10-08,P\n192311002,2026-10-08,A\n"
            "192311003,2026-10-08\n192311004,2026-10-08,L\n")
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as tmp:
        tmp.write(data)
        filename = tmp.name
    try:
        print(summarise(filename))
    finally:
        os.remove(filename)
