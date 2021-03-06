"""
    pyspecific.py
    ~~~~~~~~~~~~~

    Sphinx extension with Python doc-specific markup.

    :copyright: 2008-2014 by Georg Brandl.
    :license: Python license.
"""

import inspect
from sphinx import addnodes
from sphinx.domains.python import PyModulelevel, PyClassmember
from sphinx.ext.autodoc import FunctionDocumenter, MethodDocumenter


class PyAsyncMixin(object):
    def handle_signature(self, sig, signode):
        ret = super().handle_signature(sig, signode)
        signode.insert(0, addnodes.desc_annotation('async ', 'async '))
        return ret


class PyAsyncFunction(PyAsyncMixin, PyModulelevel):
    def run(self):
        self.name = 'py:function'
        return PyModulelevel.run(self)


class PyAsyncMethod(PyAsyncMixin, PyClassmember):
    def run(self):
        self.name = 'py:method'
        return PyClassmember.run(self)


class PyGeneratorMixin(object):
    def handle_signature(self, sig, signode):
        ret = super().handle_signature(sig, signode)
        signode.insert(0, addnodes.desc_annotation('generator ', 'generator '))
        return ret


class PyGeneratorFunction(PyGeneratorMixin, PyModulelevel):
    def run(self):
        self.name = 'py:function'
        return PyModulelevel.run(self)


class PyGeneratorMethod(PyGeneratorMixin, PyClassmember):
    def run(self):
        self.name = 'py:method'
        return PyClassmember.run(self)


class PyTaskMixin(object):
    def handle_signature(self, sig, signode):
        ret = super().handle_signature(sig, signode)
        signode.insert(0, addnodes.desc_annotation('task ', 'task '))
        return ret


class PyTaskFunction(PyTaskMixin, PyModulelevel):
    def run(self):
        self.name = 'py:function'
        return PyModulelevel.run(self)


class PyTaskMethod(PyTaskMixin, PyClassmember):
    def run(self):
        self.name = 'py:method'
        return PyClassmember.run(self)


class FunctionDocumenter(FunctionDocumenter):
    """
    Specialized Documenter subclass for coroutines.
    """

    def import_object(self):
        ret = super().import_object()
        if self.directivetype in ('task',
                                  'async',
                                  'coroutine',
                                  'generator'):
            return ret
        obj = self.parent.__dict__.get(self.object_name)
        if getattr(obj, '_is_task', False):
            self.directivetype = 'task'
            self.member_order = self.member_order + 2
        elif inspect.iscoroutinefunction(obj):
            self.directivetype = 'async'
            self.member_order = self.member_order + 2
        elif getattr(obj, '_is_coroutine', False):
            self.directivetype = 'async'
            self.member_order = self.member_order - 2
        elif inspect.isgeneratorfunction(obj):
            self.directivetype = 'generator'
            self.member_order = self.member_order + 3
        return ret


class MethodDocumenter(MethodDocumenter):
    """
    Specialized Documenter subclass for coroutines methods.
    """

    def import_object(self):
        ret = super().import_object()
        if self.directivetype in ('taskmethod',
                                  'asyncmethod',
                                  'coroutinemethod',
                                  'generatormethod'):
            return ret
        obj = self.parent.__dict__.get(self.object_name)
        if getattr(obj, '_is_task', False):
            self.directivetype = 'taskmethod'
            self.member_order = self.member_order - 2
        elif inspect.iscoroutinefunction(obj):
            self.directivetype = 'asyncmethod'
            self.member_order = self.member_order + 2
        elif getattr(obj, '_is_coroutine', False):
            self.directivetype = 'asyncmethod'
            self.member_order = self.member_order - 2
        elif inspect.isgeneratorfunction(obj):
            self.directivetype = 'generatormethod'
            self.member_order = self.member_order + 3
        return ret


def setup(app):
    app.add_directive_to_domain('py', 'async', PyAsyncFunction)
    app.add_directive_to_domain('py', 'asyncmethod', PyAsyncMethod)

    app.add_directive_to_domain('py', 'generator', PyGeneratorFunction)
    app.add_directive_to_domain('py', 'generatormethod', PyGeneratorMethod)

    app.add_directive_to_domain('py', 'task', PyTaskFunction)
    app.add_directive_to_domain('py', 'taskmethod', PyTaskMethod)

    app.add_autodocumenter(FunctionDocumenter)
    app.add_autodocumenter(MethodDocumenter)
