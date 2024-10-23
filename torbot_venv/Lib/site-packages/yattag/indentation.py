import re
from typing import Any
from typing import Dict
from typing import List
from typing import Set
from typing import Tuple
from typing import Union

# options for the indentation of text inside of xml or html nodes
# solving issue https://github.com/leforestier/yattag/issues/38
# while maintaining compatibility with older versions of yattag
NO = False
FIRST_LINE = True
EACH_LINE = 2

__all__ = ['indent', 'NO', 'FIRST_LINE', 'EACH_LINE']

class TokenMeta(type):

    _token_classes = {}  # type: Dict[str, 'TokenBase']

    def __new__(cls, name, bases, attrs):
        # type: (str, Tuple[Any], Dict[str, Any]) -> Any
        kls = type.__new__(cls, name, bases, attrs)
        cls._token_classes[name] = kls
        return kls

    @classmethod
    def getclass(cls, name):
        # type: (str) -> Any
        return cls._token_classes[name]

# need to proceed that way for Python 2/3 compatility:
TokenBase = TokenMeta('TokenBase', (object,), {}) # type: Any

class Token(TokenBase): # type: ignore
    regex = None # type: Union[None, str]

    def __init__(self, groupdict):
        # type: (Dict[str, Any]) -> None
        self.content = groupdict[self.__class__.__name__]

class Text(Token):
    regex = '[^<>]+'
    def __init__(self, *args, **kwargs):
        # type: (Dict[str, Any], Any) -> None
        super(Text, self).__init__(*args, **kwargs)
        self._isblank = None # type: Union[None, bool]

    @property
    def isblank(self):
        # type: () -> bool
        if self._isblank is None:
            self._isblank = not self.content.strip()
        return self._isblank

class Comment(Token):
    regex = r'<!--((?!-->).)*.?-->'

class CData(Token):
    regex = r'<!\[CDATA\[(.*?)\]\]>'

class Doctype(Token):
    regex = r'''<!DOCTYPE(\s+([^<>"']+|"[^"]*"|'[^']*'))*>'''

_open_tag_start = r'''
    <\s*
        (?P<{tag_name_key}>{tag_name_rgx})
        (\s+[^/><"=\s]+     # attribute
            (\s*=\s*
                (
                    [^/><"=\s]+ |    # unquoted attribute value
                    ("[^"]*") |    # " quoted attribute value
                    ('[^']*')      # ' quoted attribute value
                )
            )?  # the attribute value is optional (we're forgiving)
        )*
    \s*'''

class Script(Token):
    _end_script = r'<\s*/\s*script\s*>'

    regex = _open_tag_start.format(
        tag_name_key = 'script_ignore',
        tag_name_rgx = 'script',
    ) + r'>((?!({end_script})).)*.?{end_script}'.format(
        end_script = _end_script
    )

class Style(Token):
    _end_style = r'<\s*/\s*style\s*>'

    regex = _open_tag_start.format(
        tag_name_key = 'style_ignore',
        tag_name_rgx = 'style',
    ) + r'>((?!({end_style})).)*.?{end_style}'.format(
        end_style = _end_style
    )

class XMLDeclaration(Token):
    regex = _open_tag_start.format(
        tag_name_key = 'xmldecl_ignore',
        tag_name_rgx = r'\?\s*xml'
    ) + r'\?\s*>'

class XMLProcessingInstruction(Token):
    regex = r'<\?(?!xml\s)[^?/><"\s]+(\s[^?>]*)?\?>'

class NamedTagTokenMeta(TokenMeta):
    def __new__(cls, name, bases, attrs):
        # type: (str, Tuple[Any], Dict[str, Any]) -> Any
        kls = TokenMeta.__new__(cls, name, bases, attrs)
        if name not in('NamedTagTokenBase', 'NamedTagToken'):
            kls.tag_name_key = 'tag_name_%s' % name
            kls.regex = kls.regex_template.format(
                tag_name_key = kls.tag_name_key,
                tag_name_rgx = kls.tag_name_rgx
            )
        return kls

# need to proceed that way for Python 2/3 compatility
NamedTagTokenBase = NamedTagTokenMeta(
    'NamedTagTokenBase',
    (Token,),
    {'tag_name_rgx': r'[^?/><"\s]+'}
)

class NamedTagToken(NamedTagTokenBase): # type: ignore
    def __init__(self, groupdict):
        # type: (Dict[str, Any]) -> None
        super(NamedTagToken, self).__init__(groupdict)
        self.tag_name = groupdict[self.__class__.tag_name_key]

class OpenTag(NamedTagToken):
    regex_template = _open_tag_start + '>'

class SelfTag(NamedTagToken): # a self closing tag
    regex_template = _open_tag_start + r'/\s*>'

class CloseTag(NamedTagToken):
    regex_template = r'<\s*/(?P<{tag_name_key}>{tag_name_rgx})(\s[^/><"]*)?>'

class XMLTokenError(Exception):
        pass

class Tokenizer(object):

    def __init__(self, token_classes):
        # type: (Tuple[Any, ...]) -> None
        self.token_classes = token_classes
        self.token_names = [kls.__name__ for kls in token_classes]
        self.get_token = None # type: Any

    def _compile_regex(self):
        # type: () -> None
        self.get_token = re.compile(
            '|'.join(
                '(?P<%s>%s)' % (klass.__name__, klass.regex) for klass in self.token_classes
            ),
            re.X | re.I | re.S
        ).match

    def tokenize(self, string):
        # type: (str) -> List[Any]
        if not self.get_token:
            self._compile_regex()
        result = [] # type: List[Any]
        append = result.append
        start = 0
        l = len(string)
        while start < l:
            mobj = self.get_token(string, start)
            if mobj:
                groupdict = mobj.groupdict()
                class_name = next(name for name in self.token_names if groupdict[name])
                token = TokenMeta.getclass(class_name)(groupdict)
                append(token)
                start += len(token.content)
            else:
                raise XMLTokenError("Unrecognized XML token near %s" % repr(string[:100]))

        return result

tokenize = Tokenizer(
    (Text, Comment, CData, Doctype, XMLDeclaration, Script, Style, OpenTag, SelfTag, CloseTag, XMLProcessingInstruction)
).tokenize

class TagMatcher(object):

    class SameNameMatcher(object):
        def __init__(self):
            # type: () -> None
            self.unmatched_open = [] # type: List[Any]
            self.matched = {} # type: Dict[str, Any]

        def sigclose(self, i):
            # type: (Any) -> Any
            if self.unmatched_open:
                open_tag = self.unmatched_open.pop()
                self.matched[open_tag] = i
                self.matched[i] = open_tag
                return open_tag
            else:
                return None

        def sigopen(self, i):
            # type: (Any) -> Any
            self.unmatched_open.append(i)

    def __init__(self, token_list, blank_is_text = False):
        # type: (List[Any], bool) -> None
        self.token_list = token_list
        self.name_matchers = {} # type: Dict[str, Any]
        self.direct_text_parents = set() # type: Set[Any]

        for i in range(len(token_list)):
            token = token_list[i]
            tpe = type(token)
            if tpe is OpenTag:
                self._get_name_matcher(token.tag_name).sigopen(i)
            elif tpe is CloseTag:
                self._get_name_matcher(token.tag_name).sigclose(i)

        # TODO move this somewhere else
        current_nodes = []
        for i in range(len(token_list)):
            token = token_list[i]
            tpe = type(token)
            if tpe is OpenTag and self.ismatched(i):
                current_nodes.append(i)
            elif tpe is CloseTag and self.ismatched(i):
                current_nodes.pop()
            elif tpe is Text and (blank_is_text or not token.isblank):
                if current_nodes:
                    self.direct_text_parents.add(current_nodes[-1])

    def _get_name_matcher(self, tag_name):
        # type: (str) -> Any
        try:
            return self.name_matchers[tag_name]
        except KeyError:
            self.name_matchers[tag_name] = name_matcher = self.__class__.SameNameMatcher()
            return name_matcher

    def ismatched(self, i):
        # type: (Any) -> bool
        return i in self.name_matchers[self.token_list[i].tag_name].matched

    def directly_contains_text(self, i):
        # type: (Any) -> bool
        return i in self.direct_text_parents

new_line_rgx= re.compile(r'(\r?\n)', flags = re.MULTILINE)

def indent(string, indentation = '  ', newline = '\n', indent_text = NO, blank_is_text = False):
    # type: (str, str, str, bool, bool) -> Any
    """
    takes a string representing a html or xml document and returns
     a well indented version of it

    arguments:
    - string: the string to process
    - indentation: the indentation unit (default to two spaces)
    - newline: the string to be use for new lines
      (default to  '\\n', could be set to '\\r\\n' for example)
    - indent_text:
        the value of this option should one of yattag.NO, yattag.FIRST_LINE or yattag.EACH_LINE

        if indent_text is NO, text nodes won't be indented, and the content
         of any node directly containing text will be unchanged:

            <p>Hello</p> will be unchanged

            <p><strong>Hello</strong> world!</p> will be unchanged
             since ' world!' is directly contained in the <p> node.

            This is the default since that's generally what you want for HTML.

        if indent_text is FIRST_LINE, the first line of text nodes will be indented:

            <p>Hello</p>

            would result in

            <p>
              hello
            </p>

            and:

            <p>Hello,
            where are the keys?</p>

            would result in

            <p>
              hello,
            where are the keys?
            </p>

        if indent_text is EACH_LINE, each line inside the text nodes will be indented:

            <code class="scala-source">
            object HelloWorld {
                def main(args: Array[String]) {
                    println("Hello, world!")
                }
            }
            </code>

            would result in

            <code class="scala-source">

              object HelloWorld {
                  def main(args: Array[String]) {
                      println("Hello, world!")
                  }
              }

            </code>

    - blank_is_text:
        if False, completely blank texts are ignored. That is the default.
    """
    tokens = tokenize(string)
    tag_matcher = TagMatcher(tokens, blank_is_text = blank_is_text)
    ismatched = tag_matcher.ismatched
    directly_contains_text = tag_matcher.directly_contains_text
    result = [] # type: List[Any]
    append = result.append
    level = 0
    sameline = 0
    was_just_opened = False
    tag_appeared = False
    def _indent():
        # type: () -> None
        if tag_appeared:
            append(newline)
        for i in range(level):
            append(indentation)
    def _append_text(text):
        # type: (str) -> None
        if not sameline:
            _indent()
        if indent_text is EACH_LINE:
            append(new_line_rgx.sub(r'\1' + indentation * level, text))
        else:
            append(text)
    for i,token in enumerate(tokens):
        tpe = type(token)
        if tpe is Text:
            if blank_is_text or not token.isblank:
                _append_text(token.content)
                was_just_opened = False
        elif tpe is OpenTag and ismatched(i):
            was_just_opened = True
            if sameline:
                sameline += 1
            else:
                _indent()
            if indent_text is NO and directly_contains_text(i):
                sameline = sameline or 1
            append(token.content)
            level += 1
            tag_appeared = True
        elif tpe is CloseTag and ismatched(i):
            level -= 1
            tag_appeared = True
            if sameline:
                sameline -= 1
            elif not was_just_opened:
                _indent()
            append(token.content)
            was_just_opened = False
        else:
            if not sameline:
                _indent()
            append(token.content)
            was_just_opened = False
            tag_appeared = True
    return ''.join(result)

if __name__ == '__main__':
    import sys
    print(indent(sys.stdin.read()))
