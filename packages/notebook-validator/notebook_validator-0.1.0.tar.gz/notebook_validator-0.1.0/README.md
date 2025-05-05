
# Fabric Notebook Validator

A Python library for validating Microsoft Fabric notebooks against coding standards and naming conventions using natural language prompts.

## Features

- Check Python notebook cells against established coding standards
- Validate naming conventions for variables, functions, and classes
- Use natural language to specify validation requirements
- Get detailed reports on issues found in notebook cells

## Usage

```python
from fabric_notebook_validator import validate_with_prompt

# Run validation with natural language
results = validate_with_prompt("Check if my notebook follows all the Python coding standards")

# Display results
display_validation_results(results)
