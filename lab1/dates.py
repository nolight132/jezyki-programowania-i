def parse_date(date_str):
    """
    Converts a date in the format 'DD-MM-YYYY' into a dictionary.
    """
    day, month, year = map(int, date_str.split('-'))
    return {"day": day, "month": month, "year": year}


def compare_dates(date1, date2):
    """
    Compares two dates stored as dictionaries.
    Returns:
    - True if date1 > date2
    - False if date1 <= date2
    """
    if date1["year"] != date2["year"]:
        return date1["year"] > date2["year"]
    if date1["month"] != date2["month"]:
        return date1["month"] > date2["month"]
    return date1["day"] > date2["day"]


def bubble_sort_dates(dates):
    """
    Sorts a list of dates in ascending order using the bubble sort algorithm.
    """
    n = len(dates)
    for i in range(n):
        for j in range(0, n - i - 1):
            # Compare adjacent dates
            if compare_dates(dates[j], dates[j + 1]):
                # Swap if they are in the wrong order
                dates[j], dates[j + 1] = dates[j + 1], dates[j]


def main():
    n = int(input("Enter the number of dates to sort: "))

    dates = []
    for _ in range(n):
        date_str = input("Enter a date in the format DD-MM-YYYY: ")
        dates.append(parse_date(date_str))

    bubble_sort_dates(dates)

    print("\nSorted dates:")
    for date in dates:
        print(f"{date['day']:02d}-{date['month']:02d}-{date['year']}")


if __name__ == "__main__":
    main()
