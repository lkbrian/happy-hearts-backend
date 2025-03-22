from datetime import date, datetime


def calculate_age(Date_Of_birth):
    # Parse the date string to a date object
    try:
        birth_date = datetime.strptime(Date_Of_birth, "%Y-%m-%d").date()
    except ValueError:
        print("\033[91m Invalid date format. Use YYYY-MM-DD. \033[0m")
        return

    if birth_date < date.today():
        current_date = date.today()
        years = current_date.year - birth_date.year
        months = current_date.month - birth_date.month
        days = current_date.day - birth_date.day

        if months < 0 or (months == 0 and days < 0):
            years -= 1
            if months < 0:
                months += 12
            else:
                months = 11
            if days < 0:
                days += 30

        weeks = days // 7
        days %= 7

        return f"{years}years, {months}months, {weeks}weeks, {days}days"
    else:
        print("\033[91m Enter a past date \033[0m")


# Example usage
# age = calculate_age("2011/08/07")
# if age:
#     print(f"Years: {age[0]}, Months: {age[1]}, Weeks: {age[2]}, Days: {age[3]}")
