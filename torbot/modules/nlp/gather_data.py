import csv
import os

from pathlib import Path

os.chdir(Path(__file__).parent)


def write_data():
    """
    Writes the training data from the csv file to a directory based on the
    scikit-learn.datasets `load_files` specification.

    dataset source: https://www.kaggle.com/hetulmehta/website-classification

    e.g.
    container_folder/
            category_1_folder/
                    file_1.txt file_2.txt file_3.txt ... file_42.txt
            category_2_folder/
                    file_43.txt file_44.txt ...
    """

    with open("website_classification.csv") as csvfile:
        website_reader = csv.reader(csvfile, delimiter=",")
        for row in website_reader:
            [id, website, content, category] = row
            if category != "category":
                category = category.replace("/", "+")
            dir_name = f"training_data/{category}"
            Path(dir_name).mkdir(parents=True, exist_ok=True)
            with open(f"{dir_name}/{id}.txt", mode="w+") as txtfile:
                txtfile.write(content)


if __name__ == "__main__":
    write_data()
