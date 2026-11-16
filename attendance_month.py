from pathlib import Path
from collections import defaultdict
import csv

def process_month(input_dir, report_dir, total_working_days):
    input_dir, report_dir = Path(input_dir), Path(report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    counts = defaultdict(lambda: {"P": 0, "A": 0})
    errors = []

    for path in sorted(input_dir.glob("*.txt")):
        try:
            with path.open("r", encoding="utf-8") as file:
                for line_no, raw in enumerate(file, 1):
                    line = raw.strip()
                    if not line:
                        errors.append((path.name, line_no, "blank line"))
                        continue
                    fields = [x.strip() for x in line.split(",")]
                    if len(fields) != 3:
                        errors.append((path.name, line_no, "expected 3 fields"))
                        continue
                    reg, date, status = fields
                    if status not in {"P", "A"}:
                        errors.append((path.name, line_no, f"invalid status {status!r}"))
                        continue
                    counts[reg][status] += 1
        except (OSError, UnicodeDecodeError) as exc:
            errors.append((path.name, 0, f"{type(exc).__name__}: {exc}"))

    with (report_dir / "attendance_percentages.csv").open("w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(["register_number", "present", "absent", "percentage"])
        for reg in sorted(counts):
            p, a = counts[reg]["P"], counts[reg]["A"]
            pct = (p / total_working_days * 100) if total_working_days else 0
            writer.writerow([reg, p, a, f"{pct:.2f}"])

    with (report_dir / "below_75.txt").open("w", encoding="utf-8") as out:
        for reg in sorted(counts):
            pct = counts[reg]["P"] / total_working_days * 100 if total_working_days else 0
            if pct < 75:
                out.write(f"{reg},{pct:.2f}%\n")

    with (report_dir / "damaged_lines.csv").open("w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(["file_name", "line_number", "reason"])
        writer.writerows(errors)
    return counts, errors

if __name__ == "__main__":
    counts, errors = process_month("daily_files", "reports", 20)
    print("Students processed:", len(counts))
    print("Damaged records:", len(errors))
    print("Reports written to reports/")
