from pathlib import Path

def save_returns(books, log_path="returns.log"):
    with open(log_path, "a", encoding="utf-8") as log:
        for book in books:
            if book:
                log.write(book.rstrip("\n") + "\n")

def process(day_file, log_path="returns.log", error_path="errors.log"):
    try:
        with open(day_file, "r", encoding="utf-8") as source:
            books = [line.strip() for line in source if line.strip()]
        save_returns(books, log_path)
    except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as exc:
        with open(error_path, "a", encoding="utf-8") as errors:
            errors.write(f"{day_file}: {type(exc).__name__}: {exc}\n")
        return False
    return True

if __name__ == "__main__":
    for day in ("day1.txt", "day2.txt", "day3.txt"):
        print(day, "OK" if process(day) else "FAILED")
    print(Path("returns.log").read_text(encoding="utf-8"))
