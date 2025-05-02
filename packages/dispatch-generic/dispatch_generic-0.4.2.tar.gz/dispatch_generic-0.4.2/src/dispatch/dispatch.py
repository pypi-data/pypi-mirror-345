import inspect
from bisect import insort_right

from typeguard import TypeCheckError, check_type

_Parameter = inspect.Parameter
_empty = _Parameter.empty


def _check_type(value, _type):
    try:
        check_type(value, _type)
    except TypeCheckError:
        return False
    return True


class Dispatcher:
    def __init__(self, name):
        self.name = name
        self._signatures = []
        self._use_preference = False
        self._quick_dispatches = set()
        self._cache = {}
        self.doc = None

    def register(self, function, preference=None, quick_dispatch=False):
        if quick_dispatch:
            self._quick_dispatches.add(id(function))
        signature = inspect.signature(function)
        if preference is None:
            preference = len(self._signatures)
        else:
            self._use_preference = True
        item = (preference, signature, function)
        if self._use_preference:
            insort_right(self._signatures, item, key=lambda x: x[0])
        else:
            self._signatures.append(item)
        self.doc = None

    @staticmethod
    def check_signature(signature: inspect.Signature, args: tuple, kwargs: dict) -> bool:
        try:
            bind = signature.bind(*args, **kwargs)
        except TypeError:
            return False
        parameters = signature.parameters
        for name, value in bind.arguments.items():
            parameter = parameters[name]
            annotation = parameter.annotation
            if annotation is _empty:
                continue
            kind = parameter.kind
            if kind == _Parameter.VAR_POSITIONAL:
                for arg in value:
                    if not _check_type(arg, annotation):
                        return False
            elif kind == _Parameter.VAR_KEYWORD:
                for kwarg in value.values():
                    if not _check_type(kwarg, annotation):
                        return False
            elif not _check_type(value, annotation):
                return False
        return True

    def __call__(self, *args, **kwargs):
        args_key = tuple(map(type, args))
        kwargs_key = frozenset((key, type(value)) for key, value in kwargs.items())
        key = (args_key, kwargs_key)
        function = self._cache.get(key)
        if function is not None:
            return function(*args, **kwargs)
        for _, signature, function in reversed(self._signatures):
            if self.check_signature(signature, args, kwargs):
                if id(function) in self._cache:
                    self._cache[key] = function
                return function(*args, **kwargs)
        raise TypeError(args, kwargs)

    def get_doc_blocks(self):
        if self._use_preference:
            for preference, signature, function in self._signatures:
                yield f'preference: {preference}\n\n{signature}\n{function.__doc__}' if function.__doc__ else signature
        else:
            for _, signature, function in self._signatures:
                yield f'{signature}\n{function.__doc__}' if function.__doc__ else str(signature)

    @property
    def __doc__(self):
        if self.doc is None:
            self.doc = f'A dispatcher for {self.name}()\nIncluding:\n\n' + '\n\n'.join(self.get_doc_blocks())
        return self.doc

    def __str__(self):
        return f'<Dispatcher for {self.name}>'

    def __repr__(self):
        return f'<Dispatcher for {self.name}>'

    def __len__(self):
        return len(self._signatures)


def __iter__(self):
    return (function for _, _, function in self._signatures)


class Dispatch:
    def __init__(self):
        self._dispatchers = {}

    def dispatcher_register(self, function, qualname, module, preference, quick_dispatch):
        qualname = qualname or function.__qualname__
        module = module or function.__module__
        key = (qualname, module)
        dispatcher = self._dispatchers.get(key)
        if dispatcher is None:
            name = qualname if module == '__main__' else f'{module}.{qualname}'
            dispatcher = self._dispatchers[key] = Dispatcher(name)
        dispatcher.register(function, preference, quick_dispatch)
        return dispatcher

    def __call__(self, function=None, *, qualname=None, module=None, preference=None, quick_dispatch=False):
        if function is not None:
            return self.dispatcher_register(function, qualname, module, preference, quick_dispatch)

        def dispatch_wrapper(_function, _qualname=qualname, _module=module, _preference=preference,
                             _quick_dispatch=quick_dispatch):
            return self.dispatcher_register(_function, _qualname, _module, _preference, _quick_dispatch)

        return dispatch_wrapper
