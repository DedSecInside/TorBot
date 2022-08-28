"""
Test module for saving data to file
"""
import json
import os
from ..savefile import saveJson


def test_save_json_successful():
    """
    Sucessfully create and dump JSON object of links
    """
    mock_data = [
        'http://aff.ironsocket.com/SH7L', 'http://aff.ironsocket.com/SH7L', 'http://wsrs.net/', 'http://cmsgear.com/'
    ]
    try:
        file_name = saveJson('Links', mock_data)
        mock_output = {'Links': mock_data}

        with open('test_file.json', 'w+') as test_file:
            json.dump(mock_output, test_file, indent=2)

        os.chdir(os.getcwd())
        assert os.path.isfile(file_name) is True
        mock_file = open(file_name, 'r')
        test_file = open('test_file.json', 'r')

        mock_data = mock_file.read()
        test_data = test_file.read()

    finally:
        os.remove(file_name)
        os.remove('test_file.json')

    assert mock_data == test_data


if __name__ == '__main__':
    test_save_json_successful()
