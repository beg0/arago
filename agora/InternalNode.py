# vim: set syntax=python:
# vim: set ts=4 sts=4 sw=4 et:
# AGORA Another Generator Of Rest Api
# (c) 2018 - beg0
#

from __future__ import print_function
import re

from six import string_types

from agora.HttpMethods import METHOD_TO_FUNCTIONS

VARNAME_RE = re.compile("^\\$\\{(.*)\\}$")

class InternalMethod(object):
    """ Method to generate a resource request for a given verb

    Used by InternalNode """
    def __init__(self, verb, **kwargs):
        self.verb = verb.upper()

        if 'mime' in kwargs:
            self.request_mime = self.response_mime = kwargs['mime']
            del kwargs['mime']
        else:
            self.request_mime = self.response_mime = None

        if 'request_mime' in kwargs:
            self.request_mime = kwargs['request_mime']
            del kwargs['request_mime']
        else:
            self.request_mime = None

        if 'resonse_mime' in kwargs:
            self.response_mime = kwargs['response_mime']
            del kwargs['response_mime']
        else:
            self.response_mime = None

        if kwargs:
            raise LookupError("Unknown methods parameters: " + ", ".join(kwargs.keys()))

    def __eq__(self, other):
        if not isinstance(other, InternalMethod):
            # Uncomment to debug equality
            #print("other type is %r" % type(other))
            return False

        for attr in ["verb", "request_mime", "response_mime"]:
            if self.__getattribute__(attr) != other.__getattribute__(attr):
                # Uncomment to debug equality
                #print("%s differents: %r vs %r" % \
                #     (attr, self.__getattribute__(attr), other.__getattribute__(attr)))
                return False
        return True

class InternalNode(object):
    """ Node used internally by ResourceNode
    This node are created by parsers such as SimpleApiParser

    Unlike MethodNode object, this one don't play with __getattr__() and __call__() to defines
    tree components.
    All children nodes are defined in dictionaries. It it then easier to manipulate, but less
    sexy. That's why it is used internally
    """
    def __init__(self, name, parent):
        self.children = {}
        self.param_children = {}
        self.methods = []
        self.name = name
        self.parent = parent
        self.input_validator = {}

        self.doc = None
        varmatch = VARNAME_RE.match(self.name)
        if varmatch:
            self.varname = varmatch.group(1)
        else:
            self.varname = None

    def add_child(self, name):
        """ Add a child resource to this node """
        varmatch = VARNAME_RE.match(name)

        dest = self.children
        key = name
        if varmatch is not None:
            dest = self.param_children
            key = varmatch.group(1)

        if key in dest:
            return dest[key]

        dest[key] = InternalNode(name, self)
        return dest[key]

    def add_method(self, verb, **kwargs):
        """ Add a VERB to this node """
        if verb.upper() not in METHOD_TO_FUNCTIONS:
            raise ValueError("bad method %s" % verb)

        method = InternalMethod(verb.upper(), **kwargs)

        if method not in self.methods:
            self.methods.append(method)
            self.methods = sorted(self.methods, key=lambda e: e.verb)

    def is_placeholder(self):
        """ Tell if this resource name is a variable """
        return self.varname is not None

    def get_url(self):
        """ Get full url of this resource """
        if self.parent is not None:
            return self.parent.get_url() + "/" + self.name
        return self.name

    def set_doc(self, docstring):
        """ Set documentation associated with this resource """
        if docstring is None or isinstance(docstring, string_types):
            self.doc = docstring
        else:
            raise ValueError("bad type for doc: got " + type(docstring).__name__ + ", expected string")


    def __eq__(self, other):
        if not isinstance(other, InternalNode):
            # Uncomment to debug equality
            #print("other type is %r" % type(other))
            return False

        for attr in ["name", "children", "param_children", "methods",
                     "input_validator", "doc", "varname"]:
            if self.__getattribute__(attr) != other.__getattribute__(attr):
                # Uncomment to debug equality
                #print("%s: %s differents: %r vs %r" % \
                #     (self.name, attr, self.__getattribute__(attr), other.__getattribute__(attr)))
                return False
        return True
