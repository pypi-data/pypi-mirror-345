import ast
import re
from collections import Counter

def check_line_length(content):
    issues = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if len(line) > 80 and not line.strip().startswith('#'):
            issues.append({
                "rule": "line_length",
                "line_number": i + 1,
                "message": "Line exceeds 80 characters",
                "code": line
            })
    return issues

def check_global_keyword(content):
    issues = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "global" in line and not line.strip().startswith("#"):
            issues.append({
                "rule": "global_keyword",
                "line_number": i + 1,
                "message": "Avoid using global keyword",
                "code": line.strip()
            })
    return issues

def check_docstrings(content):
    issues = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not ast.get_docstring(node):
                issues.append({
                    "rule": "missing_docstring",
                    "line_number": node.lineno,
                    "message": f"Missing docstring for {'function' if isinstance(node, ast.FunctionDef) else 'class'} '{node.name}'",
                    "code": f"{'def' if isinstance(node, ast.FunctionDef) else 'class'} {node.name}"
                })
    except SyntaxError:
        pass
    return issues

def check_imports(content):
    issues = []
    lines = content.split('\n')
    found_non_import = False
    for i, line in enumerate(lines):
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.strip().startswith(('import ', 'from ')):
            if found_non_import:
                issues.append({
                    "rule": "import_placement",
                    "line_number": i + 1,
                    "message": "Imports should be at the top of the file",
                    "code": line.strip()
                })
        else:
            found_non_import = True
    return issues

def check_semicolon(content):
    issues = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if ';' in line and not line.strip().startswith("#"):
            issues.append({
                "rule": "semicolon_usage",
                "line_number": i + 1,
                "message": "Avoid using semicolons in Python",
                "code": line.strip()
            })
    return issues

def check_indentation(content):
    issues = []
    lines = content.split('\n')
    space_indent = []
    tab_indent = []

    for i, line in enumerate(lines):
        if line.startswith(' '):
            space_indent.append(i + 1)
        elif line.startswith('\t'):
            tab_indent.append(i + 1)

    if space_indent and tab_indent:
        for line_num in tab_indent:
            issues.append({
                "rule": "mixed_indentation",
                "line_number": line_num,
                "message": "Avoid mixing tabs and spaces for indentation",
                "code": lines[line_num - 1]
            })

    return issues

def get_all_rule_functions():
    return [
        check_line_length,
        check_global_keyword,
        check_docstrings,
        check_imports,
        check_semicolon,
        check_indentation
    ]
