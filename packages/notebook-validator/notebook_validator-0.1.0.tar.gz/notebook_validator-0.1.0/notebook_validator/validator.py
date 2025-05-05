from .parsers.notebook_parser import NotebookParser
from .rules.coding_standards import get_all_rule_functions
from .rules.naming_rules import (
    check_variable_names, 
    check_function_names, 
    check_class_names
    )

def validate_notebook(notebook_path):
    parser = NotebookParser()
    cells = parser.parse_notebook(notebook_path)
    all_issues = []

    rule_functions = get_all_rule_functions()
    for cell in cells:
        content = cell["content"]
        for rule_func in rule_functions:
            all_issues.extend(rule_func(content))

        all_issues.extend(check_variable_names(content))
        all_issues.extend(check_function_names(content))
        all_issues.extend(check_class_names(content))
    
    return all_issues

def validate_with_prompt(prompt, notebook_path=None):
    if notebook_path is None:
        try:
            notebook_path = NotebookParser().get_current_notebook_path()
        except Exception:
            # Fallback: try first notebook in current folder
            import glob, os
            notebooks = glob.glob("*.ipynb")
            if notebooks:
                notebook_path = os.path.abspath(notebooks[0])
            else:
                raise FileNotFoundError("No .ipynb notebook file found. Please pass notebook_path manually.")

    return validate_notebook(notebook_path)