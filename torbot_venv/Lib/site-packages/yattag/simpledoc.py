__all__ = ['SimpleDoc']

import re
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple
from typing import Union
from typing import cast

class DocError(Exception):
    pass

class SimpleDoc(object):

    """
    class generating xml/html documents using context managers

    doc, tag, text = SimpleDoc().tagtext()

    with tag('html'):
        with tag('body', id = 'hello'):
            with tag('h1'):
                text('Hello world!')

    print(doc.getvalue())
    """

    class Tag(object):
        def __init__(self, doc, name, attrs): # name is the tag name (ex: 'div')
            # type: (SimpleDoc, str, Dict[str, Union[str, int, float]]) -> None

            self.doc = doc
            self.name = name
            self.attrs = attrs

        def __enter__(self):
            # type: () -> None
            self.parent_tag = self.doc.current_tag
            self.doc.current_tag = self
            self.position = len(self.doc.result)
            self.doc._append('')

        def __exit__(self, tpe, value, traceback):
            # type: (Any, Any, Any) -> None
            if value is None:
                if self.attrs:
                    self.doc.result[self.position] = "<%s %s>" % (
                        self.name,
                        dict_to_attrs(self.attrs),
                    )
                else:
                    self.doc.result[self.position] = "<%s>" % self.name
                self.doc._append("</%s>" % self.name)
                self.doc.current_tag = self.parent_tag

    class DocumentRoot(object):

        class DocumentRootError(DocError, AttributeError):
            # Raising an AttributeError on __getattr__ instead of just a DocError makes it compatible
            # with the pickle module (some users asked for pickling of SimpleDoc instances).
            # I also keep the DocError from earlier versions to avoid possible compatibility issues
            # with existing code.
            pass

        def __getattr__(self, item):
            # type: (str) -> Any
            raise SimpleDoc.DocumentRoot.DocumentRootError("DocumentRoot here. You can't access anything here.")

    _newline_rgx = re.compile(r'\r?\n')

    def __init__(self, stag_end = ' />', nl2br = False):
        # type: (str, bool) -> None
        r"""
            stag_end:
                the string terminating self closing tags.
                This determines what tags produced using the `stag` method will look like.
                For example, if you set `stag_end='>'`, then `doc.stag('hr')` will
                produce a `<hr>` tag.
                If you set `stag_end=' />'` (the default), then `doc.stag('hr')` would
                instead produce a `<hr />` tag.
                If you set `nl2br=True`, then the `text` method will also
                produce `<br>` or `<br />` tags according to this preference when encountering
                new lines.
                Defaults to ' />'.

            nl2br:
                if set to True, the `text` method will turn new lines
                ('\n' or '\r\n' sequences) in the input to `<br />` html tags,
                or possibly to `<br>` tags if using the `stag_end` parameter to this effect.
                (see explanations about `stag_end` above).
                Defaults to False (new lines are not replaced).

        """
        self.result = [] # type: List[str]
        self.current_tag = self.__class__.DocumentRoot() # type: Any
        self._append = self.result.append
        assert stag_end in (' />', '/>', '>')
        self._stag_end = stag_end
        self._br = '<br' + stag_end
        self._nl2br = nl2br

    def tag(self, tag_name, *args, **kwargs):
        # type: (str, Tuple[str, Union[str, int, float]], Union[str, int, float]) -> Tag
        """
        opens a HTML/XML tag for use inside a `with` statement
        the tag is closed when leaving the `with` block
        HTML/XML attributes can be supplied as keyword arguments,
        or alternatively as (key, value) pairs.
        The values of the keyword arguments should be strings.
        They are escaped for use as HTML attributes
        (the " character is replaced with &quot;)

        In order to supply a "class" html attributes, you must supply a `klass` keyword
        argument. This is because `class` is a reserved python keyword so you can't use it
        outside of a class definition.

        Example::

            with tag('h1', id = 'main-title'):
                text("Hello world!")

            # <h1 id="main-title">Hello world!</h1> was appended to the document

            with tag('td',
                ('data-search', 'lemon'),
                ('data-order', '1384'),
                id = '16'
            ):
                text('Citrus Limon')

            # you get: <td data-search="lemon" data-order="1384" id="16">Citrus Limon</td>

        """
        return self.__class__.Tag(self, tag_name, _attributes(args, kwargs))


    def text(self, *strgs):
        # type: (str) -> None
        r"""
        appends 0 or more strings to the document
        the strings are escaped for use as text in html documents, that is,
        & becomes &amp;
        < becomes &lt;
        > becomes &gt;

        Example::

            username = 'Max'
            text('Hello ', username, '!') # appends "Hello Max!" to the current node
            text('16 > 4') # appends "16 &gt; 4" to the current node

        New lines ('\n' or '\r\n' sequences) are left intact, unless you have set the
        nl2br option to True when creating the SimpleDoc instance. Then they would be
        replaced with `<br />` tags (or `<br>` tags if using the `stag_end` option
        of the SimpleDoc constructor as shown in the example below).

        Example::

            >>> doc = SimpleDoc()
            >>> doc.text('pistachio\nice cream')
            >>> doc.getvalue()
            'pistachio\nice cream'

            >>> doc = SimpleDoc(nl2br=True)
            >>> doc.text('pistachio\nice cream')
            >>> doc.getvalue()
            'pistachio<br />ice cream'

            >>> doc = SimpleDoc(nl2br=True, stag_end='>')
            >>> doc.text('pistachio\nice cream')
            >>> doc.getvalue()
            'pistachio<br>ice cream'

        """
        for strg in strgs:
            transformed_string = html_escape(strg)
            if self._nl2br:
                self._append(
                    self.__class__._newline_rgx.sub(
                        self._br,
                        transformed_string
                    )
                )
            else:
                self._append(transformed_string)

    def line(self, tag_name, text_content, *args, **kwargs):
        # type: (str, str, Tuple[str, Union[str, int, float]], Union[str, int, float]) -> None
        """
        Shortcut to write tag nodes that contain only text.
        For example, in order to obtain::

            <h1>The 7 secrets of catchy titles</h1>

        you would write::

            line('h1', 'The 7 secrets of catchy titles')

        which is just a shortcut for::

            with tag('h1'):
                text('The 7 secrets of catchy titles')

        The first argument is the tag name, the second argument
        is the text content of the node.
        The optional arguments after that are interpreted as xml/html
        attributes. in the same way as with the `tag` method.

        Example::

            line('a', 'Who are we?', href = '/about-us.html')

        produces::

            <a href="/about-us.html">Who are we?</a>
        """
        with self.tag(tag_name, *args, **kwargs):
            self.text(text_content)

    def asis(self, *strgs):
        # type: (str) -> None
        """
        appends 0 or more strings to the documents
        contrary to the `text` method, the strings are appended "as is"
        &, < and > are NOT escaped

        Example::

            doc.asis('<!DOCTYPE html>') # appends <!DOCTYPE html> to the document
        """
        for strg in strgs:
            if strg is None:
                raise TypeError("Expected a string, got None instead.")
                # passing None by mistake was frequent enough to justify a check
                # see https://github.com/leforestier/yattag/issues/20
            self._append(strg)

    def nl(self):
        # type: () -> None
        self._append('\n')

    def attr(self, *args, **kwargs):
        # type: (Tuple[str, Union[str, int, float]], Union[str, int, float]) -> None
        """
        sets HTML/XML attribute(s) on the current tag
        HTML/XML attributes are supplied as (key, value) pairs of strings,
        or as keyword arguments.
        The values of the keyword arguments should be strings.
        They are escaped for use as HTML attributes
        (the " character is replaced with &quot;)
        Note that, instead, you can set html/xml attributes by passing them as
        keyword arguments to the `tag` method.

        In order to supply a "class" html attributes, you can either pass
        a ('class', 'my_value') pair, or supply a `klass` keyword argument
        (this is because `class` is a reserved python keyword so you can't use it
        outside of a class definition).

        Examples::

            with tag('h1'):
                text('Welcome!')
                doc.attr(id = 'welcome-message', klass = 'main-title')

            # you get: <h1 id="welcome-message" class="main-title">Welcome!</h1>

            with tag('td'):
                text('Citrus Limon')
                doc.attr(
                    ('data-search', 'lemon'),
                    ('data-order', '1384')
                )


            # you get: <td data-search="lemon" data-order="1384">Citrus Limon</td>

        """
        self.current_tag.attrs.update(_attributes(args, kwargs))

    def data(self, *args, **kwargs):
        # type: (Tuple[str, Union[str, int, float]], Union[str, int, float]) -> None
        """
        sets HTML/XML data attribute(s) on the current tag
        HTML/XML data attributes are supplied as (key, value) pairs of strings,
        or as keyword arguments.
        The values of the keyword arguments should be strings.
        They are escaped for use as HTML attributes
        (the " character is replaced with &quot;)
        Note that, instead, you can set html/xml data attributes by passing them as
        keyword arguments to the `tag` method.

        Examples::

            with tag('h1'):
                text('Welcome!')
                doc.data(msg='welcome-message')

            # you get: <h1 data-msg="welcome-message">Welcome!</h1>

            with tag('td'):
                text('Citrus Limon')
                doc.data(
                    ('search', 'lemon'),
                    ('order', '1384')
                )


            # you get: <td data-search="lemon" data-order="1384">Citrus Limon</td>

        """
        self.attr(
            *(('data-%s' % key, value) for (key, value) in args),
            **dict(('data-%s' % key, value) for (key, value) in kwargs.items())
        )

    def stag(self, tag_name, *args, **kwargs):
        # type: (str, Tuple[str, Union[str, int, float]], Union[str, int, float]) -> None
        """
        appends a self closing tag to the document
        html/xml attributes can be supplied as keyword arguments,
        or alternatively as (key, value) pairs.
        The values of the keyword arguments should be strings.
        They are escaped for use as HTML attributes
        (the " character is replaced with &quot;)

        Example::

            doc.stag('img', src = '/salmon-plays-piano.jpg')
            # appends <img src="/salmon-plays-piano.jpg" /> to the document

        If you want to produce self closing tags without the ending slash (HTML5 style),
        use the stag_end parameter of the SimpleDoc constructor at the creation of the
        SimpleDoc instance.

        Example::

            >>> doc = SimpleDoc(stag_end = '>')
            >>> doc.stag('br')
            >>> doc.getvalue()
            '<br>'
        """
        if args or kwargs:
            self._append("<%s %s%s" % (
                tag_name,
                dict_to_attrs(_attributes(args, kwargs)),
                self._stag_end
            ))
        else:
            self._append("<%s%s" % (tag_name, self._stag_end))

    def cdata(self, strg, safe = False):
        # type: (str, bool) -> None
        """
        appends a CDATA section containing the supplied string

        You don't have to worry about potential ']]>' sequences that would terminate
        the CDATA section. They are replaced with ']]]]><![CDATA[>'.

        If you're sure your string does not contain ']]>', you can pass `safe = True`.
        If you do that, your string won't be searched for ']]>' sequences.
        """
        self._append('<![CDATA[')
        if safe:
            self._append(strg)
        else:
            self._append(strg.replace(']]>', ']]]]><![CDATA[>'))
        self._append(']]>')

    def getvalue(self):
        # type: () -> str
        """
        returns the whole document as a single string
        """
        return ''.join(self.result)

    def tagtext(self):
        # type: () -> Tuple[SimpleDoc, Any, Any]
        """
        return a triplet composed of::
            . the document itself
            . its tag method
            . its text method

        Example::

            doc, tag, text = SimpleDoc().tagtext()

            with tag('h1'):
                text('Hello world!')

            print(doc.getvalue()) # prints <h1>Hello world!</h1>
        """

        return self, self.tag, self.text

    def ttl(self):
        # type: () -> Tuple[SimpleDoc, Any, Any, Any]
        """
        returns a quadruplet composed of::
            . the document itself
            . its tag method
            . its text method
            . its line method

        Example::

            doc, tag, text, line = SimpleDoc().ttl()

            with tag('ul', id='grocery-list'):
                line('li', 'Tomato sauce', klass="priority")
                line('li', 'Salt')
                line('li', 'Pepper')

            print(doc.getvalue())
        """
        return self, self.tag, self.text, self.line

    def add_class(self, *classes):
        # type: (str) -> None
        """
        adds one or many elements to the html "class" attribute of the current tag
        Example::
            user_logged_in = False
            with tag('a', href="/nuclear-device", klass = 'small'):
                if not user_logged_in:
                    doc.add_class('restricted-area')
                text("Our new product")

            print(doc.getvalue())

            # prints <a class="restricted-area small" href="/nuclear-device"></a>
        """
        self._set_classes(
            self._get_classes().union(classes)
        )

    def discard_class(self, *classes):
        # type: (str) -> None
        """
        remove one or many elements from the html "class" attribute of the current
        tag if they are present (do nothing if they are absent)
        """
        self._set_classes(
            self._get_classes().difference(classes)
        )

    def toggle_class(self, elem, active):
        # type: (str, bool) -> None
        """
        if active is a truthy value, ensure elem is present inside the html
        "class" attribute of the current tag, otherwise (if active is falsy)
        ensure elem is absent
        """
        classes = self._get_classes()
        if active:
            classes.add(elem)
        else:
            classes.discard(elem)
        self._set_classes(classes)


    def _get_classes(self):
        # type: () -> Set[str]
        try:
            current_classes = self.current_tag.attrs['class']
        except KeyError:
            return set()
        else:
            return set(current_classes.split())

    def _set_classes(self, classes_set):
        # type: (Set[str]) -> None
        if classes_set:
            self.current_tag.attrs['class'] = ' '.join(classes_set)
        else:
            try:
                del self.current_tag.attrs['class']
            except KeyError:
                pass

def html_escape(s):
    # type: (Union[str, int, float]) -> str
    if isinstance(s,(int,float)):
        return str(s)
    try:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    except AttributeError:
        raise TypeError(
            "You can only insert a string, an int or a float inside a xml/html text node. "
            "Got %s (type %s) instead." % (repr(s), repr(type(s)))
        )


def attr_escape(s):
    # type: (Union[str, int, float]) -> str
    if isinstance(s,(int,float)):
        return str(s)
    try:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")
    except AttributeError:
        raise TypeError(
            "xml/html attributes should be passed as strings, ints or floats. "
            "Got %s (type %s) instead." % (repr(s), repr(type(s)))
        )


ATTR_NO_VALUE = object()

def dict_to_attrs(dct):
    # type: (Dict[str, Any]) -> str
    return ' '.join(
        (key if value is ATTR_NO_VALUE
        else '%s="%s"' % (key, attr_escape(value)))
        for key,value in dct.items()
    )

def _attributes(args, kwargs):
    # type: (Any, Any) -> Dict[str, Any]
    lst = [] # type: List[Any]
    for arg in args:
        if isinstance(arg, tuple):
            lst.append(arg)
        elif isinstance(arg, str):
            lst.append((arg, ATTR_NO_VALUE))
        else:
            raise ValueError(
                "Couldn't make a XML or HTML attribute/value pair out of %s."
                % repr(arg)
            )
    result = dict(lst)
    result.update(
        (('class', value) if key == 'klass' else (key, value))
        for key,value in kwargs.items()
    )
    return result
