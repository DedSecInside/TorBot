import csv
from os import write
from pathlib import Path

"""
Writes the training data from the csv file to a directory based on the scikit-learn.datasets `load_files` specification.

dataset source: https://www.kaggle.com/hetulmehta/website-classification

e.g.
container_folder/
	category_1_folder/
		file_1.txt file_2.txt file_3.txt ... file_42.txt
	category_2_folder/
		file_43.txt file_44.txt ...
"""

def write_data():
	with open('website_classification.csv') as csvfile:
		website_reader = csv.reader(csvfile, delimiter=',')
		for row in website_reader:
			[id, website, content, category] = row
			if category != 'category':
				category = category.replace('/', '+')
				Path(f"training_data/{category}").mkdir(parents=True, exist_ok=True)
				with open(f'training_data/{category}/{id}.txt', mode='w+') as txtfile:
					txtfile.write(content)

if __name__ == "__main__":
	write_data()


