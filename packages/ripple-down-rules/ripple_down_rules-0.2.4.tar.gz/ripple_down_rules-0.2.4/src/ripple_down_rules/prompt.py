import ast
import logging
import os
import subprocess
import tempfile
from _ast import AST
from functools import cached_property
from textwrap import indent, dedent

from IPython.core.magic import register_line_magic, line_magic, Magics, magics_class
from IPython.terminal.embed import InteractiveShellEmbed
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.python import PythonLexer
from traitlets.config import Config
from typing_extensions import List, Optional, Tuple, Dict, Type, Union, Any

from .datastructures.enums import PromptFor
from .datastructures.case import Case
from .datastructures.callable_expression import CallableExpression, parse_string_to_expression
from .datastructures.dataclasses import CaseQuery
from .utils import extract_dependencies, contains_return_statement, make_set, get_imports_from_scope, make_list, \
    get_import_from_type, get_imports_from_types, is_iterable, extract_function_source, encapsulate_user_input, \
    are_results_subclass_of_types
from colorama import Fore, Style, init


@magics_class
class MyMagics(Magics):
    def __init__(self, shell, scope, output_type: Optional[Type] = None, func_name: str = "user_case",
                 func_doc: str = "User defined function to be executed on the case.",
                 code_to_modify: Optional[str] = None,
                 attribute_type_hint: Optional[str] = None,
                 prompt_for: Optional[PromptFor] = None):
        super().__init__(shell)
        self.scope = scope
        self.temp_file_path = None
        self.func_name = func_name
        self.func_doc = func_doc
        self.code_to_modify = code_to_modify
        self.attribute_type_hint = attribute_type_hint
        self.prompt_for = prompt_for
        self.output_type = make_list(output_type) if output_type is not None else None
        self.user_edit_line = 0
        self.function_signature: Optional[str] = None
        self.build_function_signature()

    @line_magic
    def edit(self, line):

        boilerplate_code = self.build_boilerplate_code()

        self.write_to_file(boilerplate_code)

        print(f"Opening {self.temp_file_path} in PyCharm...")
        subprocess.Popen(["pycharm", "--line", str(self.user_edit_line), self.temp_file_path],
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)

    def build_boilerplate_code(self):
        imports = self.get_imports()
        self.build_function_signature()
        if self.code_to_modify is not None:
            body = indent(dedent(self.code_to_modify), '    ')
        else:
            body = "    # Write your code here\n    pass"
        boilerplate = f"""{imports}\n\n{self.function_signature}\n    \"\"\"{self.func_doc}\"\"\"\n{body}"""
        self.user_edit_line = imports.count('\n')+6
        return boilerplate

    def build_function_signature(self):
        output_type_hint = ""
        if self.prompt_for == PromptFor.Conditions:
            output_type_hint = " -> bool"
        elif self.prompt_for == PromptFor.Conclusion:
            output_type_hint = f" -> {self.attribute_type_hint}"
        self.function_signature = f"def {self.func_name}(case: {self.case_type.__name__}){output_type_hint}:"

    def write_to_file(self, code: str):
        tmp = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".py",
                                          dir=os.path.dirname(self.scope['__file__']))
        tmp.write(code)
        tmp.flush()
        self.temp_file_path = tmp.name
        tmp.close()

    def get_imports(self):
        case_type_import = f"from {self.case_type.__module__} import {self.case_type.__name__}"
        if self.output_type is None:
            output_type_imports = [f"from typing_extensions import Any"]
        else:
            output_type_imports = get_imports_from_types(self.output_type)
            if len(self.output_type) > 1:
                output_type_imports.append("from typing_extensions import Union")
            if list in self.output_type:
                output_type_imports.append("from typing_extensions import List")
        imports = get_imports_from_scope(self.scope)
        imports = [i for i in imports if ("get_ipython" not in i)]
        if case_type_import not in imports:
            imports.append(case_type_import)
        imports.extend([oti for oti in output_type_imports if oti not in imports])
        imports = set(imports)
        return '\n'.join(imports)

    @cached_property
    def case_type(self) -> Type:
        """
        Get the type of the case object in the current scope.

        :return: The type of the case object.
        """
        case = self.scope['case']
        return case._obj_type if isinstance(case, Case) else type(case)

    @line_magic
    def load(self, line):
        if not self.temp_file_path:
            print(f"{Fore.RED}ERROR:: No file to load. Run %edit first.{Style.RESET_ALL}")
            return

        with open(self.temp_file_path, 'r') as f:
            source = f.read()

        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == self.func_name:
                exec_globals = {}
                exec(source, self.scope, exec_globals)
                user_function = exec_globals[self.func_name]
                self.shell.user_ns[self.func_name] = user_function
                print(f"{Fore.BLUE}Loaded `{self.func_name}` function into user namespace.{Style.RESET_ALL}")
                return

        print(f"{Fore.RED}ERROR:: Function `{self.func_name}` not found.{Style.RESET_ALL}")

    @line_magic
    def help(self, line):
        """
        Display help information for the Ipython shell.
        """
        help_text = f"""
Directly write python code in the shell, and then `{Fore.GREEN}return {Fore.RESET}output`. Or use 
the magic commands to write the code in a temporary file and edit it in PyCharm:
{Fore.MAGENTA}Usage: %edit{Style.RESET_ALL}
Opens a temporary file in PyCharm for editing a function (conclusion or conditions for case)
 that will be executed on the case object.
{Fore.MAGENTA}Usage: %load{Style.RESET_ALL}
Loads the function defined in the temporary file into the user namespace, that can then be used inside the
 Ipython shell. You can then do `{Fore.GREEN}return {Fore.RESET}function_name(case)`.
        """
        print(help_text)


class CustomInteractiveShell(InteractiveShellEmbed):
    def __init__(self, output_type: Union[Type, Tuple[Type], None] = None, func_name: Optional[str] = None,
                 func_doc: Optional[str] = None, code_to_modify: Optional[str] = None,
                 attribute_type_hint: Optional[str] = None, prompt_for: Optional[PromptFor] = None, **kwargs):
        super().__init__(**kwargs)
        keys = ['output_type', 'func_name', 'func_doc', 'code_to_modify', 'attribute_type_hint', 'prompt_for']
        values = [output_type, func_name, func_doc, code_to_modify, attribute_type_hint, prompt_for]
        magics_kwargs = {key: value for key, value in zip(keys, values) if value is not None}
        self.my_magics = MyMagics(self, self.user_ns, **magics_kwargs)
        self.register_magics(self.my_magics)
        self.all_lines = []

    def run_cell(self, raw_cell: str, **kwargs):
        """
        Override the run_cell method to capture return statements.
        """
        if contains_return_statement(raw_cell) and 'def ' not in raw_cell:
            if self.my_magics.func_name in raw_cell:
                self.all_lines = extract_function_source(self.my_magics.temp_file_path,
                                                         self.my_magics.func_name,
                                                         join_lines=False)[self.my_magics.func_name]
            self.all_lines.append(raw_cell)
            self.history_manager.store_inputs(line_num=self.execution_count, source=raw_cell)
            self.ask_exit()
            return None
        result = super().run_cell(raw_cell, **kwargs)
        if result.error_in_exec is None and result.error_before_exec is None:
            self.all_lines.append(raw_cell)
        return result


class IPythonShell:
    """
    Create an embedded Ipython shell that can be used to prompt the user for input.
    """

    def __init__(self, scope: Optional[Dict] = None, header: Optional[str] = None,
                 prompt_for: Optional[PromptFor] = None, case_query: Optional[CaseQuery] = None,
                 code_to_modify: Optional[str] = None):
        """
        Initialize the Ipython shell with the given scope and header.

        :param scope: The scope to use for the shell.
        :param header: The header to display when the shell is started.
        :param prompt_for: The type of information to ask the user about.
        :param case_query: The case query which contains the case and the attribute to ask about.
        :param code_to_modify: The code to modify. If given, will be used as a start for user to modify.
        """
        self.scope: Dict = scope or {}
        self.header: str = header or ">>> Embedded Ipython Shell"
        output_type = None
        if prompt_for is not None:
            if prompt_for == PromptFor.Conclusion and case_query is not None:
                output_type = case_query.attribute_type
            elif prompt_for == PromptFor.Conditions:
                output_type = bool
        self.case_query: Optional[CaseQuery] = case_query
        self.output_type: Optional[Type] = output_type
        self.prompt_for: Optional[PromptFor] = prompt_for
        self.code_to_modify: Optional[str] = code_to_modify
        self.user_input: Optional[str] = None
        self.func_name: str = ""
        self.func_doc: str = ""
        self.shell: CustomInteractiveShell = self._init_shell()
        self.all_code_lines: List[str] = []

    def _init_shell(self):
        """
        Initialize the Ipython shell with a custom configuration.
        """
        cfg = Config()
        self.build_func_name_and_doc()
        shell = CustomInteractiveShell(config=cfg, user_ns=self.scope, banner1=self.header,
                                       output_type=self.output_type, func_name=self.func_name, func_doc=self.func_doc,
                                       code_to_modify=self.code_to_modify,
                                       attribute_type_hint=self.case_query.attribute_type_hint,
                                       prompt_for=self.prompt_for)
        return shell

    def build_func_name_and_doc(self) -> Tuple[str, str]:
        """
        Build the function name and docstring for the user-defined function.

        :return: A tuple containing the function name and docstring.
        """
        case = self.scope['case']
        case_type = case._obj_type if isinstance(case, Case) else type(case)
        self.func_name = self.build_func_name(case_type)
        self.func_doc = self.build_func_doc(case_type)

    def build_func_doc(self, case_type: Type) -> Optional[str]:
        if self.case_query is None or self.prompt_for is None:
            return

        if self.prompt_for == PromptFor.Conditions:
            func_doc = (f"Get conditions on whether it's possible to conclude a value"
                        f" for {case_type.__name__}.{self.case_query.attribute_name}")
        elif self.prompt_for == PromptFor.Conclusion:
            func_doc = f"Get possible value(s) for {case_type.__name__}.{self.case_query.attribute_name}"
        else:
            return

        possible_types = [t.__name__ for t in self.case_query.attribute_type if t not in [list, set]]
        if list in self.case_query.attribute_type:
            func_doc += f" of type list of {' and/or '.join(possible_types)}"
        else:
            func_doc += f" of type(s) {', '.join(possible_types)}"

        return func_doc

    def build_func_name(self, case_type: Type) -> Optional[str]:
        func_name = None
        if self.prompt_for is not None:
            func_name = f"get_{self.prompt_for.value.lower()}_for"
            func_name += f"_{case_type.__name__}"

        if self.case_query is not None:
            func_name += f"_{self.case_query.attribute_name}"
            output_names = [f"{t.__name__}" for t in self.case_query.attribute_type if t not in [list, set]]
            func_name += '_of_type_' + '_'.join(output_names)

        return func_name.lower() if func_name is not None else None

    def run(self):
        """
        Run the embedded shell.
        """
        while True:
            try:
                self.shell()
                self.update_user_input_from_code_lines()
                break
            except Exception as e:
                logging.error(e)
                print(f"{Fore.RED}ERROR::{e}{Style.RESET_ALL}")

    def update_user_input_from_code_lines(self):
        """
        Update the user input from the code lines captured in the shell.
        """
        if len(self.shell.all_lines) == 1 and self.shell.all_lines[0].replace('return', '').strip() == '':
            self.user_input = None
        else:
            self.all_code_lines = extract_dependencies(self.shell.all_lines)
            if len(self.all_code_lines) == 1 and self.all_code_lines[0].strip() == '':
                self.user_input = None
            else:
                self.user_input = '\n'.join(self.all_code_lines)
                self.user_input = encapsulate_user_input(self.user_input, self.shell.my_magics.function_signature,
                                                         self.func_doc)
                if f"return {self.func_name}(case)" not in self.user_input:
                    self.user_input = self.user_input.strip() + f"\nreturn {self.func_name}(case)"


def prompt_user_for_expression(case_query: CaseQuery, prompt_for: PromptFor, prompt_str: Optional[str] = None)\
        -> Tuple[Optional[str], Optional[CallableExpression]]:
    """
    Prompt the user for an executable python expression to the given case query.

    :param case_query: The case query to prompt the user for.
    :param prompt_for: The type of information ask user about.
    :param prompt_str: The prompt string to display to the user.
    :return: A callable expression that takes a case and executes user expression on it.
    """
    prev_user_input: Optional[str] = None
    callable_expression: Optional[CallableExpression] = None
    while True:
        user_input, expression_tree = prompt_user_about_case(case_query, prompt_for, prompt_str,
                                                             code_to_modify=prev_user_input)
        prev_user_input = '\n'.join(user_input.split('\n')[2:-1])
        if user_input is None:
            if prompt_for == PromptFor.Conclusion:
                print(f"{Fore.YELLOW}No conclusion provided. Exiting.{Style.RESET_ALL}")
                return None, None
            else:
                print(f"{Fore.RED}Conditions must be provided. Please try again.{Style.RESET_ALL}")
                continue
        conclusion_type = bool if prompt_for == PromptFor.Conditions else case_query.attribute_type
        callable_expression = CallableExpression(user_input, conclusion_type, expression_tree=expression_tree,
                                                 scope=case_query.scope)
        try:
            result = callable_expression(case_query.case)
            if len(make_list(result)) == 0:
                print(f"{Fore.YELLOW}The given expression gave an empty result for case {case_query.name}."
                      f" Please modify!{Style.RESET_ALL}")
                continue
            break
        except Exception as e:
            logging.error(e)
            print(f"{Fore.RED}{e}{Style.RESET_ALL}")
    return user_input, callable_expression


def prompt_user_about_case(case_query: CaseQuery, prompt_for: PromptFor,
                           prompt_str: Optional[str] = None,
                           code_to_modify: Optional[str] = None) -> Tuple[Optional[str], Optional[AST]]:
    """
    Prompt the user for input.

    :param case_query: The case query to prompt the user for.
    :param prompt_for: The type of information the user should provide for the given case.
    :param prompt_str: The prompt string to display to the user.
    :param code_to_modify: The code to modify. If given will be used as a start for user to modify.
    :return: The user input, and the executable expression that was parsed from the user input.
    """
    if prompt_str is None:
        if prompt_for == PromptFor.Conclusion:
            prompt_str = f"Give possible value(s) for:\n"
        else:
            prompt_str = f"Give conditions on when can the rule be evaluated for:\n"
        prompt_str += (f"{Fore.CYAN}{case_query.name}{Fore.MAGENTA} of type(s) "
                       f"{Fore.CYAN}({', '.join(map(lambda x: x.__name__, case_query.core_attribute_type))}){Fore.MAGENTA}")
        if prompt_for == PromptFor.Conditions:
            prompt_str += (f"\ne.g. `{Fore.GREEN}return {Fore.BLUE}len{Fore.RESET}(case.attribute) > {Fore.BLUE}0` "
                           f"{Fore.MAGENTA}\nOR `{Fore.GREEN}return {Fore.YELLOW}True`{Fore.MAGENTA} (If you want the"
                           f" rule to be always evaluated) \n"
                           f"You can also do {Fore.YELLOW}%edit{Fore.MAGENTA} for more complex conditions.")
    prompt_str = f"{Fore.MAGENTA}{prompt_str}{Fore.YELLOW}\n(Write %help for guide){Fore.RESET}"
    scope = {'case': case_query.case, **case_query.scope}
    shell = IPythonShell(scope=scope, header=prompt_str, prompt_for=prompt_for, case_query=case_query,
                         code_to_modify=code_to_modify)
    return prompt_user_input_and_parse_to_expression(shell=shell)


def prompt_user_input_and_parse_to_expression(shell: Optional[IPythonShell] = None,
                                              user_input: Optional[str] = None)\
        -> Tuple[Optional[str], Optional[ast.AST]]:
    """
    Prompt the user for input.

    :param shell: The Ipython shell to use for prompting the user.
    :param user_input: The user input to use. If given, the user input will be used instead of prompting the user.
    :return: The user input and the AST tree.
    """
    while True:
        if user_input is None:
            shell = IPythonShell() if shell is None else shell
            shell.run()
            user_input = shell.user_input
            if user_input is None:
                return None, None
            print(f"{Fore.BLUE}Captured User input: {Style.RESET_ALL}")
            highlighted_code = highlight(user_input, PythonLexer(), TerminalFormatter())
            print(highlighted_code)
        try:
            return user_input, parse_string_to_expression(user_input)
        except Exception as e:
            msg = f"Error parsing expression: {e}"
            logging.error(msg)
            print(f"{Fore.RED}{msg}{Style.RESET_ALL}")
            user_input = None
