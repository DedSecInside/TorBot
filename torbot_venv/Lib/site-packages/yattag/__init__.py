"""
The SimpleDoc class generates xml or html documents using context managers (`with` blocks).
The Doc class extends the SimpleDoc class. It adds the capability to render
html forms with defaults values and errors.
These two classes can be used to define html templates in a web application.

Basic example
-------------

Nested html tags, no need to close tags.

.. code:: python

    from yattag import Doc

    doc, tag, text = Doc().tagtext()

    with tag('html'):
        with tag('body', id = 'hello'):
            with tag('h1'):
                text('Hello world!')

    print(doc.getvalue())

Html form rendering example with default values
-----------------------------------------------

.. code:: python

    from yattag import Doc

    doc, tag, text = Doc(
        defaults = {'ingredient': ['chocolate', 'coffee']}
    ).tagtext()

    with tag('form', action = ""):
        with tag('label'):
            text("Select one or more ingredients")
        with doc.select(name = 'ingredient', multiple = "multiple"):
            for value, description in (
                ("chocolate", "Dark chocolate"),
                ("almonds", "Roasted almonds"),
                ("honey", "Acacia honey"),
                ("coffee", "Ethiopian coffee")
            ):
                with doc.option(value = value):
                    text(description)
        doc.stag('input', type = "submit", value = "Validate")

    print(doc.getvalue())

Full tutorial on yattag.org_

.. _yattag.org: https://www.yattag.org
"""

__author__ = "Benjamin Le Forestier (benjamin@leforestier.org)"
__version__ = '1.15.1'

from yattag.simpledoc import SimpleDoc
from yattag.doc import Doc
from yattag.indentation import indent, NO, FIRST_LINE, EACH_LINE
