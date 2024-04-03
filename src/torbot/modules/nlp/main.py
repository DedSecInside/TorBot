import numpy as np
import os
from pathlib import Path

from bs4 import BeautifulSoup
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.datasets import load_files


def classify(data):
    """
    Classify URL specified by user
    """
    soup = BeautifulSoup(data, features="html.parser")
    html = soup.get_text()

    # create classifier
    clf = Pipeline(
        [
            ("vect", CountVectorizer()),
            ("tfidf", TfidfTransformer()),
            ("clf", SGDClassifier()),
        ]
    )
    try:
        os.chdir(Path(__file__).parent)

        dataset = load_files("training_data")
    except FileNotFoundError:
        print("Training data not found. Obtaining training data...")
        print("This may take a while...")
        from .gather_data import write_data

        write_data()
        print("Training data obtained.")
        dataset = load_files("training_data")
        pass
    x_train, x_test, y_train, y_test = train_test_split(dataset.data, dataset.target)
    clf.fit(x_train, y_train)

    # returns an array of target_name values
    predicted = clf.predict([html])
    accuracy = np.mean(predicted == y_test)

    return [dataset.target_names[predicted[0]], accuracy]
