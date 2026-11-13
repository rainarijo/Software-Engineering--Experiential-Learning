def parse_booking(text):
    pet, days = text.split(':')
    return pet.strip().title(), float(days)

def stay_average(days_csv):
    values = [int(r) for r in days_csv.split(',')]
    return sum(values) // len(values)

def payable_fee(text):
    fee, discount = text.split('|')
    total = float(fee) * 1.18 - float(discount)
    return max(total, 0)

def main():
    print("==== Running parse_booking ====")
    user_input = input("Enter pet:days (e.g. dog:5): ")
    result = parse_booking(user_input)
    print("Pet and Days:", result)

    print("\n==== Running stay_average ====")
    user_input = input("Enter stay lengths in days as CSV (e.g. 2,5,7): ")
    result = stay_average(user_input)
    print("Average Stay:", result)

    print("\n==== Running payable_fee ====")
    user_input = input("Enter fee|discount (e.g. 1500|100): ")
    result = payable_fee(user_input)
    print("Payable Fee:", result)

if __name__ == "__main__":
    main()
