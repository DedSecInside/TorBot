# Natural Language Processing Library

This library provides tool for performing natural language processing on websites.
This library is in it's infancy currently and can only be used for testing.

To test gathering data use:
`python3 gater_data.py`
* This will generate the data necessary to train the classification model 

To predict the classification of a webiste use:
`python3 main.py -website https://www.github.com` 
* Add `-accuracy` argument, to view the accuracy of the prediction
