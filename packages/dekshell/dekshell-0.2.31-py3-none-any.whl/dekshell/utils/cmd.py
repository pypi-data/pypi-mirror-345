import re
import sys
from dektools.escape.str import str_escape_one_type
from dektools.str import shlex_quote

key_arg = '__arg'
key_args = f'{key_arg}s'
key_kwargs = '__kwargs'
key_argv = f'{key_arg}v'


def cmd2ak(argv):  # arg0 arg-\-1 k0--kwarg0 k1--kwarg1
    args = []
    kwargs = {}
    for x in argv:
        if re.match(r'[^\W\d]\w*--', x):
            k, v = x.split('--', 1)
            kwargs[k] = v
        else:
            args.append(str_escape_one_type(x, '-', '-'))
    return args, kwargs


def ak2cmd(args=None, kwargs=None):
    result = []
    if args:
        for arg in args:
            arg = arg.replace('--', r'-\-')
            result.append(shlex_quote(arg))
    if kwargs:
        for k, v in kwargs.items():
            result.append(shlex_quote(f'{k}--{v}'))
    return ' '.join(result)


def pack_context(args, kwargs):
    return {
        **{f'{key_arg}{i}': arg for i, arg in enumerate(args)}, **{key_args: tuple(args), key_kwargs: kwargs}, **kwargs}


def pack_context_argv():
    return {**{f"{key_argv}{i}": x for i, x in enumerate(sys.argv)}, **{key_argv: sys.argv}}


def pack_context_full(args=None, kwargs=None):
    return {**pack_context(args or [], kwargs or {}), **pack_context_argv()}
