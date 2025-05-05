def display_validation_results(results):
    """Display the validation issues in a readable format.

    Args:
        results (list): A list of dictionaries containing rule violations.
    """
    if not results:
        print("✅ No issues found. Your notebook looks good!")
        return

    print(f"❌ Found {len(results)} issue(s):\n")
    for issue in results:
        line_info = f"Line {issue.get('line_number', '?')}"
        rule = issue.get("rule", "Unknown Rule")
        message = issue.get("message", "No description provided")
        code = issue.get("code", "")

        print(f"[{rule}] {line_info}: {message}")
        if code:
            print(f"  ↳ Code: {code}")
        print()
