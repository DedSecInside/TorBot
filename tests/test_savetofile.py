import sys
import os
import json
PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(
             os.path.join(os.getcwd(), os.path.expanduser(__file__))))

sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from modules import savefile


def test_save_links_successful():
    mock_data = ['http://aff.ironsocket.com/SH7L',
                 'http://aff.ironsocket.com/SH7L',
                 'http://wsrs.net/',
                 'http://cmsgear.com/']
    try:
        file_name = savefile.saveJson('Links', mock_data)
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
