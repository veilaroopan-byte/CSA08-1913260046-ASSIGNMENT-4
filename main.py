from attendance import read_records, totals, absent_three_consecutive, write_summary, write_three_absent

if __name__ == "__main__":
    records = read_records("daily_files")
    summary = totals(records)
    write_summary(summary, "summary.csv")
    write_three_absent(absent_three_consecutive(records), "three_day_absentees.txt")
    print("Processed", len(summary), "students")
