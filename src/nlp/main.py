import argparse
import requests
import numpy as np

from bs4 import BeautifulSoup
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.datasets import load_files

# get html for site
parser = argparse.ArgumentParser(description='Classify Website')
parser.add_argument('-website', type=str, help='Website to categorize')
parser.add_argument('-accuracy', type=bool, help='Print accuracy')
args = parser.parse_args()
soup = BeautifulSoup(requests.get(args.website).text, features='html.parser')
html = soup.get_text()

# create classifier
clf = Pipeline([
    ('vect', CountVectorizer()),
    ('tfidf', TfidfTransformer()),
    ('clf', SGDClassifier())
])
dataset = load_files('training_data')
x_train, x_test, y_train, y_test = train_test_split(dataset.data, dataset.target)
clf.fit(x_train, y_train)

# returns an array of target_name indices
predicted = clf.predict([html])

website = 'Unknown'
if soup.title:
    website = soup.title.text
print(f'The category of {website} is {dataset.target_names[predicted[0]]}');

if args.accuracy:
    accuracy = np.mean(predicted == y_test)
    print(f'Accuracy: {accuracy}%')

