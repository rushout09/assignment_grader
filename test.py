import csv
import random


def get_random_question(csv_file='questions.csv'):
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        random_row = random.choice(rows)
        formatted_question = (f"Topic: {random_row['Topic']}\nQuestion: {random_row['Question']}\nOptions:\nA) "
                              f"{random_row['Option A']}\nB) {random_row['Option B']}\nC) {random_row['Option C']}\nD) "
                              f"{random_row['Option D']}\nCorrect Option: {random_row['Correct Option']}\nAnswer: "
                              f"{random_row['Answer']}")
        return formatted_question


print(get_random_question())
