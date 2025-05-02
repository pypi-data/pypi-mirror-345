from os import path
from typing import Sequence
from os import path
from re import compile, sub, escape, IGNORECASE
from textwrap import indent

from sqlcompose.core.circular_dependency_error import CircularDependencyError
from sqlcompose.core.include import Include
from sqlcompose.core.compat import fix_path, get_relative_path

REGEX_INCLUDE = compile(r"\$INCLUDE\(([^\)]+)\)", IGNORECASE)


def loads(sql: str) -> str:
    """Compose SQL

    Args:
        sql (str): The query text

    Returns:
        str: The composed query
    """
    return compose(sql, "SQL", path.curdir, path.curdir)


def load(filename: str) -> str:
    """Compose SQL

    Args:
        filename (str): The path of the file containing the SQL

    Returns:
        str: The composed query
    """


    filename = fix_path(filename)

    if not path.isfile(filename):
        raise FileNotFoundError(filename)


    with open(filename, "r", encoding="utf-8") as file:
        return compose(file.read(), filename, filename, path.dirname(filename))


def compose(
    sql: str,
    name: str,
    file_path: str,
    root: str,
    level: int = 1,
    stack: list[str] | None = None
) -> str:

    file_path = fix_path(file_path)
    stack = stack or []
    parent = stack[-1] if stack else None
    name = get_relative_path(name, root)
    index = 1
    included: list[str] = []
    includes: list[Include] = []
    stack.append(name)

    if len(stack) > 1 and name in (stack[1:-1]):
        raise CircularDependencyError

    for match in REGEX_INCLUDE.finditer(sql):
        file_path_inner = fix_path(path.join(path.dirname(file_path), match.group(1)))
        if file_path_inner not in included:
            included.append(file_path_inner)
            try:
                with open(file_path_inner, "r", encoding="utf-8") as file:
                    composed = compose(
                        file.read(),
                        match.group(1),
                        file_path_inner,
                        root,
                        level + 1,
                        stack
                    )
                includes.append(
                    Include(
                        composed,
                        f"Q_{level}_{index}",
                        match.group(0),
                        match.group(1)
                    )
                )
                index = index + 1
            except FileNotFoundError:
                if parent is not None:
                    raise FileNotFoundError(f"Include failed: File \"{get_relative_path(file_path_inner, root)}\" which was referred to in \"{get_relative_path(parent, root)}\", was not found...")
                else:
                    raise FileNotFoundError(f"Include failed: File \"{get_relative_path(file_path_inner, root)}\" was not found...")

    for include in includes:
        sql = sub(escape(include.match), include.name, sql)

    stack.pop()

    return wrap_cte_sql(includes, sql, level, name)

def wrap_cte_sql(includes: Sequence[Include], sql: str, level: int, source: str) -> str:
    sql_output = ""
    indent_str = "  "

    if len(includes) > 0:
        for include in includes:
            sql_output = "WITH " if sql_output == "" else sql_output + ", "
            sql_output = f"{sql_output}{include.name} AS (\n{include.sql}\n)"

        sql_output = sql_output + ", Q_{0} AS (\n{1}\n)\nSELECT * FROM Q_{0}".format(level, indent("--{1}\n{0}".format(sql, source), indent_str)) #+ "\.format(level)
    else:
        sql_output = f"--{source}\n{sql}"

    return sql_output if level == 1 else indent(sql_output, indent_str)




