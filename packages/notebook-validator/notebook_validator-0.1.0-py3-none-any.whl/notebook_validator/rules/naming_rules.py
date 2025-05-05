import ast

def check_variable_names(content):
    issues = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if not target.id.islower() or '-' in target.id:
                            issues.append({
                                "rule": "variable_naming",
                                "line_number": node.lineno,
                                "message": "Variable names should be lowercase with underscores",
                                "code": target.id
                            })
    except SyntaxError:
        pass
    return issues

def check_function_names(content):
    issues = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                name = node.name
                if not name.islower() or '-' in name:
                    issues.append({
                        "rule": "function_naming",
                        "line_number": node.lineno,
                        "message": "Function names should be lowercase with underscores",
                        "code": f"def {name}(...):"
                    })
    except SyntaxError:
        pass
    return issues

def check_class_names(content):
    issues = []
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                name = node.name
                if not name[0].isupper() or '_' in name:
                    issues.append({
                        "rule": "class_naming",
                        "line_number": node.lineno,
                        "message": "Class names should be in PascalCase",
                        "code": f"class {name}:"
                    })
    except SyntaxError:
        pass
    return issues
