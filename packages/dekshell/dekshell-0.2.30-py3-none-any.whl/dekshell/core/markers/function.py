from dektools.dict import assign_list
from .base import MarkerBase, MarkerWithEnd, MarkerNoTranslator, cmd_call_prefix, cmd_call_prefix_simple
from .base.core import QuitContext, get_inner_vars


class CallMarker(MarkerNoTranslator):
    tag_head = "call"

    def execute(self, context, command, marker_node, marker_set):
        expression = self.split_raw(command, 1)[-1]
        return self.execute_core(context, expression)

    def execute_core(self, context, expression):
        if expression.startswith(cmd_call_prefix):
            expression = self.translate_case(context, expression, True)
            name, args, kwargs = self.cmd_call_parse(context, expression[len(cmd_call_prefix):], False)
        elif expression.startswith(cmd_call_prefix_simple):
            expression = self.translate_case(context, expression, True)
            name, args, kwargs = self.cmd_call_parse(context, expression[len(cmd_call_prefix_simple):], True)
        else:
            name = expression[:expression.find('(')]
            args, kwargs = self.eval(context, expression, {name: lambda *a, **k: (a, k)})
        function = self.eval(context, name)
        return function.pack_variables(context, args, kwargs), function.body[:]

    @staticmethod
    def real_return_value(value):
        return QuitContext.real(value)


class Function:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

    def __call__(self, *args, **kwargs):
        context, marker_set = get_inner_vars('__inner_context__', '__inner_marker_set__')
        context = context.derive().update_variables(self.pack_variables(context, args, kwargs))
        return QuitContext.real(marker_set.node_cls.execute_nodes(context, marker_set, self.body[:]))

    def __str__(self):
        return f"{self.__class__.__name__}<{self.name}>"

    def pack_variables(self, context, args, kwargs):
        return FunctionMarker.eval(context, f"lambda {self.params}: locals()")(*args, **kwargs)


class FunctionMarker(MarkerWithEnd):
    tag_head = "function"

    def execute(self, context, command, marker_node, marker_set):
        name, params = assign_list([''] * 2, self.split_raw(command, 2)[1:])
        self.set_var_raw(context, name, Function(name, params, marker_node.children[:]))
        return []


class ReturnMarker(MarkerNoTranslator):
    tag_head = "return"

    def execute(self, context, command, marker_node, marker_set):
        args = self.split_raw(command, 1, self.tag_head)
        self.ret(self.eval_mixin(context, args[1]))


class RaiseMarker(MarkerBase):
    tag_head = "raise"

    def execute(self, context, command, marker_node, marker_set):
        args = self.split_raw(command, 1, self.tag_head)
        self.raise_(args[1])


class VarGlobalMarker(MarkerBase):
    tag_head = "global"

    def execute(self, context, command, marker_node, marker_set):
        context.variables.mark_global(self.split_raw(command, 1)[-1])


class VarNonlocalMarker(MarkerBase):
    tag_head = "nonlocal"

    def execute(self, context, command, marker_node, marker_set):
        context.variables.mark_nonlocal(self.split_raw(command, 1)[-1])


class EnvGlobalMarker(MarkerBase):
    tag_head = "global$"

    def execute(self, context, command, marker_node, marker_set):
        context.environ.mark_global(self.split_raw(command, 1)[-1])


class EnvNonlocalMarker(MarkerBase):
    tag_head = "nonlocal$"

    def execute(self, context, command, marker_node, marker_set):
        context.environ.mark_nonlocal(self.split_raw(command, 1)[-1])
