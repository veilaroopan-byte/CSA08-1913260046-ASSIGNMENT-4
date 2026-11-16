from pathlib import Path
import csv
import re

class InvalidRegistration(Exception):
    pass

def parse_registration(line):
    fields = [field.strip() for field in line.strip().split(",")]
    if len(fields) != 5:
        raise InvalidRegistration(f"expected 5 comma-separated fields, found {len(fields)}")
    reg, name, department, email, events_text = fields
    if not all((reg, name, department, email, events_text)):
        raise InvalidRegistration("one or more required fields are empty")
    # String-method validation: one @, a dot in domain, and no whitespace.
    if email.count("@") != 1 or " " in email:
        raise InvalidRegistration(f"invalid email {email!r}")
    local, domain = email.split("@")
    if not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
        raise InvalidRegistration(f"invalid email {email!r}")
    events = [event.strip() for event in events_text.split(";") if event.strip()]
    if not events:
        raise InvalidRegistration("at least one event is required")
    return {"reg": reg, "name": name, "department": department,
            "email": email, "events": events}

def process_departments(input_dir, output_dir, department_files):
    input_dir, output_dir = Path(input_dir), Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    master = {}
    errors = []
    for filename in department_files:
        path = input_dir / filename
        try:
            with path.open("r", encoding="utf-8") as f:
                for line_no, line in enumerate(f, 1):
                    try:
                        item = parse_registration(line)
                        if item["reg"] in master:
                            errors.append((filename, line_no, f"duplicate register number {item['reg']}"))
                            continue
                        master[item["reg"]] = item
                    except InvalidRegistration as exc:
                        errors.append((filename, line_no, str(exc)))
        except (FileNotFoundError, PermissionError, UnicodeDecodeError, OSError) as exc:
            errors.append((filename, 0, f"{type(exc).__name__}: {exc}"))

    with (output_dir / "master_list.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["register_number", "name", "department", "email", "events"])
        for reg in sorted(master):
            item = master[reg]
            writer.writerow([reg, item["name"], item["department"], item["email"], ";".join(item["events"])])

    event_map = {}
    for item in master.values():
        for event in item["events"]:
            event_map.setdefault(event, []).append(item)
    for event, participants in event_map.items():
        safe_name = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in event)
        with (output_dir / f"event_{safe_name}.txt").open("w", encoding="utf-8") as f:
            for item in sorted(participants, key=lambda x: x["reg"]):
                f.write(f'{item["reg"]},{item["name"]},{item["department"]}\n')

    with (output_dir / "summary.txt").open("w", encoding="utf-8") as f:
        f.write(f"Valid unique registrations: {len(master)}\n")
        f.write(f"Events: {len(event_map)}\n")
        for event, participants in sorted(event_map.items()):
            f.write(f"{event}: {len(participants)} participants\n")

    with (output_dir / "error_log.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["file_name", "line_number", "reason"])
        writer.writerows(errors)
    return master, errors

if __name__ == "__main__":
    files = ["cse.txt", "ece.txt", "mech.txt", "civil.txt", "it.txt"]
    master, errors = process_departments("department_files", "fest_output", files)
    print("Valid unique registrations:", len(master))
    print("Rejected/missing-file issues:", len(errors))
    print("Output files written to fest_output/")
