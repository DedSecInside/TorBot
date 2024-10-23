from yattag.simpledoc import dict_to_attrs, html_escape, attr_escape, SimpleDoc, DocError
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union
from typing import cast

try:
    range = xrange  # for Python 2/3 compatibility
except NameError:
    pass

__all__ = ['Doc']

class SimpleInput(object):

    """
    class representing text inputs, password inputs, hidden inputs etc...
    """
    
    def __init__(self, name, tpe, attrs):
        # type: (str, str, Dict[str, Union[str, int, float]]) -> None
        self.name = name
        self.tpe = tpe
        self.attrs = attrs
        
    def render(self, defaults, errors, error_wrapper, stag_end = ' />'):
        # type: (Dict[str, str], Dict[str, str], Tuple[str, str], str) -> str
        lst = [] # List[str]
        attrs = dict(self.attrs)
        error = errors and self.name in errors
        if error:
            _add_class(attrs, 'error')
            lst.append(error_wrapper[0])
            lst.append(html_escape(errors[self.name]))
            lst.append(error_wrapper[1])
                
        if self.name in defaults:
            if(self.tpe == 'file'):
                raise DocError('Default value for HTML form input of type "file" is not supported')

            attrs['value'] = str(defaults[self.name])
        attrs['name'] = self.name
        lst.append('<input type="%s" %s%s' % (self.tpe, dict_to_attrs(attrs), stag_end))
        
        return ''.join(lst)
        

class CheckableInput(object):
    tpe = 'checkbox'

    def __init__(self, name, attrs):
        # type: (str, Dict[str, Union[str, int, float]]) -> None
        self.name = name
        self.rank = 0
        self.attrs = attrs
        
    def setrank(self, n):
        # type: (int) -> None
        self.rank = n
    
    @classmethod
    def match(cls, default, value):
        # type: (Any, Union[str, int, float]) -> bool
        if isinstance(default, str):
            return value == default
        elif isinstance(default, (tuple, list, set)):
            return value in default
        return False
     
    def checked(self, defaults):
        # type: (Dict[str, Union[List[str], str]]) -> bool
        try:
            default = defaults[self.name]
        except KeyError:
            return False
        try:
            value = self.attrs['value']
        except KeyError:
            return False
        return self.__class__.match(default, value)    
        
    
    def render(self, defaults, errors, error_wrapper, stag_end = ' />'):
        # type: (Dict[str, Union[List[str], str]], Any, Tuple[str, str], str) -> str
        lst = []
        attrs = dict(self.attrs)
        if self.rank == 0:
            if errors and self.name in errors:
                lst.append(error_wrapper[0])
                lst.append(html_escape(errors[self.name]))
                lst.append(error_wrapper[1])
                _add_class(attrs, 'error')
        
        if self.checked(defaults):
            attrs['checked'] = 'checked'
                
        attrs['name'] = self.name
        
        lst.append('<input type="%s" %s%s' % (self.__class__.tpe, dict_to_attrs(attrs), stag_end))

        return ''.join(lst)
        

class CheckboxInput(CheckableInput):
    pass
    
class RadioInput(CheckableInput):
    tpe = 'radio'
    
    @classmethod
    def match(cls, default, value):
        # type: (Any, Union[str, int, float]) -> bool
        if isinstance(default, str):
            return value == default
        return False

def groupclass(inputclass):
    # type: (Any) -> Any

    class InputGroup(object):

        def __init__(self, name):
            # type: (str) -> None
            self.name = name
            self.n_items = 0
            
        def input(self, attrs):
            # type: (Dict[str, Union[str, int, float]]) -> Any
            input_instance = inputclass(self.name, attrs)
            input_instance.setrank(self.n_items)
            self.n_items += 1
            return input_instance

    return InputGroup

class ContainerTag(object):

    tag_name = 'textarea' 

    def __init__(self, name, attrs):
        # type: (str, Dict[str, Union[str, int, float]]) -> None
        self.name = name
        self.attrs = attrs
        
    def render(self, defaults, errors, error_wrapper, inner_content = ''):
        # type: (Dict[str, str], Dict[str, str], Tuple[str, str], str) -> str
        lst = []
        attrs = dict(self.attrs)
        if errors and self.name in errors:
            lst.append(error_wrapper[0])
            lst.append(html_escape(errors[self.name]))
            lst.append(error_wrapper[1])
            _add_class(attrs, 'error')
        attrs['name'] = self.name

        lst.append('<%s %s>' % (self.__class__.tag_name, dict_to_attrs(attrs)))
        if self.name in defaults:
            lst.append(html_escape(str(defaults[self.name])))
        else:
            lst.append(inner_content)
        
        lst.append('</%s>' % self.__class__.tag_name)

        return ''.join(lst)

class Textarea(ContainerTag):
    pass

class Select(ContainerTag):
    tag_name = 'select'


class Option(object):
    def __init__(self, name, multiple, value, attrs):
        # type: (str, str, Union[str, int, float], Dict[str, Any]) -> None
        self.name = name
        self.multiple = multiple
        self.value = value
        self.attrs = attrs

    def render(self, defaults, errors, inner_content):
        # type: (Dict[str, str], Dict[str, str], str) -> str
        selected = False        
        if self.name in defaults:
            if self.multiple:
                if self.value in defaults[self.name]:
                    selected = True
            else:
                if self.value == defaults[self.name]:
                    selected = True
        lst = ['<option value="', attr_escape(self.value), '"']
        if selected:
            lst.append(' selected="selected"')
        if self.attrs:
            lst.append(' ')
            lst.append(dict_to_attrs(self.attrs))
        lst.append('>')
        lst.append(inner_content)
        lst.append('</option>')
        return ''.join(lst)
        
def _attrs_from_args(required_keys, *args, **kwargs):
    # type: (Any, Any, Union[str, int, float]) -> List[Any]
    # need to do all this to allow specifying attributes as (key, value) pairs
    # while maintaining backward compatibility with previous versions
    # of yattag, which allowed 'name', 'type', and 'value' attributes
    # as positional or as keyword arguments
    def raise_exception(arg):
        # type: (Any) -> None
        raise ValueError(
            "Optional attributes should be passed as (key, value) pairs or as keyword arguments."
            "Got %s (type %s)" % (repr(arg), repr(type(arg)))   
        )
    limit = 0
    for arg in args:
        if isinstance(arg, tuple):
            break 
        else:
            limit += 1
    if limit > len(required_keys):
        raise_exception(args[limit-1])
    attrs = dict(zip(required_keys[:limit],args[:limit]))
    for arg in args[limit:]:
        if isinstance(arg, tuple):
            attrs[arg[0]] = arg[1]
        else:
            raise_exception(arg)
    attrs.update(
        (('class', value) if key == 'klass' else (key, value))
        for key, value in kwargs.items()
    )

    required_attrs = []

    for key in required_keys:
        try:
            required_attrs.append(attrs.pop(key))
        except KeyError:
            raise ValueError(
                "the %s attribute is missing" % repr(key)
            )
    return required_attrs + [attrs]
   
class Doc(SimpleDoc):
    """
    The Doc class extends the SimpleDoc class with form rendering capabilities. 
    Pass default values or errors as dictionnaries to the Doc constructor, and 
    use the `input`, `textarea`, `select`, `option` methods
    to append form elements to the document.
    """
    
    SimpleInput = SimpleInput
    CheckboxInput = CheckboxInput
    RadioInput = RadioInput
    Textarea = Textarea
    Select = Select
    Option = Option
    
    class TextareaTag(object):
        def __init__(self, doc, name, attrs):
            # type: (Doc, str, Dict[str, Union[str, int, float]]) -> None
            # name is the name attribute of the textarea, ex: 'contact_message'
            # for <textarea name="contact_message">
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
                inner_content = ''.join(self.doc.result[self.position+1:])
                del self.doc.result[self.position+1:]              
                rendered_textarea = self.doc.__class__.Textarea(self.name, self.attrs).render(
                    defaults = self.doc.defaults,
                    errors = self.doc.errors,
                    inner_content = inner_content,
                    error_wrapper = self.doc.error_wrapper
                )
                self.doc.result[self.position] = rendered_textarea
                self.doc.current_tag = self.parent_tag
                
    
    class SelectTag(object):
        def __init__(self, doc, name, attrs):
            # type: (Doc, str, Dict[str, Union[str, int, float]]) -> None
            # name is the name attribute of the select, ex: 'color'
            # for <select name="color">
            self.doc = doc
            self.name = name
            self.attrs = attrs
            self.multiple = bool(attrs.get('multiple'))
            self.old_current_select = None
                
        def __enter__(self):
            # type: () -> None
            self.parent_tag = self.doc.current_tag
            self.doc.current_tag = self
            self.position = len(self.doc.result)
            self.doc._append('')
            self.old_current_select = self.doc.current_select
            self.doc.current_select = self
            
        def __exit__(self, tpe, value, traceback):
            # type: (Any, Any, Any) -> None
            if value is None:
                inner_content = ''.join(self.doc.result[self.position+1:])
                del self.doc.result[self.position+1:]
                rendered_select = self.doc.__class__.Select(self.name, self.attrs).render(
                    defaults = {},  # no defaults for the <select> tag. Defaults are handled by the <option> tags directly.
                    errors = self.doc.errors,
                    inner_content = inner_content,
                    error_wrapper = self.doc.error_wrapper
                )
                self.doc.result[self.position] = rendered_select
                self.doc.current_tag = self.parent_tag  
                self.doc.current_select = self.old_current_select
                

    class OptionTag(object):
        def __init__(self, doc, select, value, attrs):
            # type: (Doc, Doc.SelectTag, str, Dict[str, Union[str, int, float]]) -> None
            self.doc = doc
            self.select = select
            self.attrs = attrs
            self.value = value

        def __enter__(self):
            # type: () -> None
            self.parent_tag = self.doc.current_tag
            self.doc.current_tag = self
            self.position = len(self.doc.result)
            self.doc._append('')
            
        def __exit__(self, tpe, value, traceback):
            # type: (Any, Any, Any) -> None
            if value is None:
                inner_content = ''.join(self.doc.result[self.position+1:])
                del self.doc.result[self.position+1:]
                self.doc.result[self.position] = self.doc.__class__.Option(
                    name = self.select.name,
                    multiple = self.select.multiple,
                    value = self.value,
                    attrs = self.attrs
                ).render(
                    defaults = self.doc.defaults,
                    errors = self.doc.errors,
                    inner_content = inner_content
                )
                self.doc.current_tag = self.parent_tag

    
    def __init__(self, defaults = None, errors = None,
     error_wrapper = ('<span class="error">', '</span>'), *args, **kwargs):
        # type: (Optional[Dict[str, str]], Optional[Dict[str, str]], Tuple[str, str], Any, Any) -> None
        """
        creates a Doc instance
        
        defaults::
            optional dictionnary of values used to fill html forms
        errors::
            optional dictionnary of errors used to fill html forms
        
        Example 1::
            doc = Doc()
        
        Example 2::
            doc = Doc(
                defaults = {
                    'beverage': 'coffee',
                    'preferences': ['milk', 'sugar'],
                    'use_discount': True
                },
                errors = {
                    'preferences': "We ran out of milk!"
                }
            )
            
        Note: very often you'll want to call the `tagtext` method just after
        creating a Doc instance. Like this::
        
        doc, tag, text = Doc(defaults = {'color': 'blue'}).tagtext()
        
        This way, you can write `tag` (resp. `text`) in place of `doc.tag`
        (resp. `doc.text`). When writing long html templates or xml documents,
        it's a gain in readability and performance.
        """
                
        super(Doc, self).__init__(*args, **kwargs)
        self.defaults = defaults or {}
        self.errors = errors or {}
        self.error_wrapper = error_wrapper
        self.radios = {} # type: Dict[str, Any]
        self.checkboxes = {} # type: Dict[str, Any]
        self.current_select = None # type: Optional[Any]
        self.radio_group_class = groupclass(self.__class__.RadioInput)
        self.checkbox_group_class = groupclass(self.__class__.CheckboxInput)
        self._fields = set() # type: Set[Any]
        self._detached_errors_pos = [] # type: List[Any]
    
     
    def input(self, *args, **kwargs):
        # type: (Any, Union[str, int, float]) -> None
        "required attributes: 'name' and 'type'"
        name, type, attrs = _attrs_from_args(('name', 'type'), *args, **kwargs)
        self._fields.add(name)
        if type in (
            'text','file','tel', 'password', 'hidden', 'search', 'email', 'url', 'number',
            'range', 'date', 'datetime', 'datetime-local', 'month', 'week',
            'time', 'color'
        ): 
            self.asis(
                self.__class__.SimpleInput(name, type, attrs).render(
                    self.defaults, self.errors, self.error_wrapper, self._stag_end
                )
            )
            return
        if type == 'radio':
            if name not in self.radios:
                self.radios[name] = self.radio_group_class(name)
            checkable_group = self.radios[name]
        elif type == 'checkbox':
            if name not in self.checkboxes:
                self.checkboxes[name] = self.checkbox_group_class(name)
            checkable_group = self.checkboxes[name]
        else:
            if type == 'submit':
                raise DocError("Unhandled input type: submit. Use doc.stag('input', type = 'submit', value='whatever') instead.")
            else:
                raise DocError("Unknown input type: %s" % type)
        
        self._append(checkable_group.input(attrs).render(self.defaults, self.errors, self.error_wrapper, self._stag_end))
        
    def textarea(self, *args, **kwargs):
        # type: (Any, Union[str, int, float]) -> Doc.TextareaTag
        "required attribute: 'name'"
        name, attrs = _attrs_from_args(('name',), *args, **kwargs)
        self._fields.add(name)
        return self.__class__.TextareaTag(self, name, attrs)
        
    def select(self, *args, **kwargs):
        # type: (Any, Union[str, int, float]) -> Doc.SelectTag
        "required attribute: 'name'"
        name, attrs = _attrs_from_args(('name',), *args, **kwargs)
        self._fields.add(name)
        return self.__class__.SelectTag(self, name, attrs)
        
    def option(self, *args, **kwargs):
        # type: (Any, Union[str, int, float]) -> Doc.OptionTag
        "required attribute: 'value'"
        if self.current_select:
            value, attrs = _attrs_from_args(('value',), *args, **kwargs)
            return self.__class__.OptionTag(self, self.current_select, value, attrs)
        else:
            raise DocError("No <select> tag opened. Can't put an <option> here.")
            
    def detached_errors(self, render_function = None):
        # type: (Any) -> None
        self._detached_errors_pos.append((len(self.result), render_function or self.error_dict_to_string))
        self.result.append('')
        
    def error_dict_to_string(self, dct):
        # type: (Dict[str, str]) -> str
        if dct:
            doc, tag, text = SimpleDoc().tagtext()
            with tag('ul', klass='error-list'):
                for error in dct.values():
                    with tag('li'):
                        text(error)
            return doc.getvalue()
        else:
            return ''
                        
            
    def getvalue(self):
        # type: () -> str
        """
        returns the whole document as a string
        """
        for position, render_function in self._detached_errors_pos:
            self.result[position] = render_function(
                dict((name, self.errors[name]) for name in self.errors if name not in self._fields)
            )
        return ''.join(self.result)

def _add_class(dct, klass):
    # type: (Dict[str, Any], str) -> None
    classes = dct.get('class', '').split()
    if klass not in classes:
        dct['class'] = ' '.join(classes + [klass])
