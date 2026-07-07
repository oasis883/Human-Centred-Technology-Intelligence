from clean_tickets import clean_tickets
from classify_behaviour import classify_file
from generate_insights import generate_report

def main():
    print("Starting HumanTech Intelligence pipeline...")
    clean_tickets()
    classify_file()
    generate_report()
    print("Done. Open reports/insights_report.md")

if __name__ == "__main__":
    main()
