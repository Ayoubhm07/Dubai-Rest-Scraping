import csv


def calculate_average_amount(filename):
    total_amount = 0
    count = 0

    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)

        for row in reader:
            if row:
                amount = float(row[10])
                total_amount += amount
                count += 1

    average_amount = total_amount / count if count > 0 else 0
    return average_amount


filename = '../real_estate_data.csv'
average_amount = calculate_average_amount(filename)
print(f"La moyenne de l'amount est: {average_amount:.2f}")  # Affichage avec 2 chiffres après la virgule
