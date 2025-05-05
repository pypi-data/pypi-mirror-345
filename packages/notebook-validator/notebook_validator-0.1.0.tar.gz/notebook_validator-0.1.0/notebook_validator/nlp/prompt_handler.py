def handle_prompt(prompt):
    """Very basic natural language prompt handler (placeholder).

    Args:
        prompt (str): Natural language prompt.

    Returns:
        dict: Simulated result or command from prompt.
    """
    # In a real implementation, this could use an LLM or rules
    prompt = prompt.strip().lower()
    
    if "coding standards" in prompt or "pep8" in prompt:
        return {"action": "validate_all_coding_rules"}
    elif "naming convention" in prompt:
        return {"action": "validate_naming"}
    elif "docstring" in prompt:
        return {"action": "check_docstrings"}
    else:
        return {"action": "validate_all"}
