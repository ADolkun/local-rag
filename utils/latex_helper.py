import re

latex_pattern = re.compile(
    """
    Note: This pattern used to match LaTeX expressions in text.
    """
    r"""
    (?P<dollar>\${1,2})(?P<dcontent>.+?)\1  # Matches $...$ or $$...$$
    |
    \\begin\{(?P<env>equation|align|gather|multline)\*?\}
        (?P<env_content>.+?)
    \\end\{(?P=env)\*?\}
    |
    \\?\[(?P<brack>.+?)\\?\]   # Matches \[...\]
    |
    \\?\((?P<inline>.+?)\\?\)  # Matches \(...\)
    |
    \\begin\{(?P<xtd_env>lemma|theorem|proof)\}
        (?P<xtd_content>.+?)
    \\end\{(?P=xtd_env)\}
    |
    \\DeclareMathOperator\*?\{(?P<decl_op>[A-Za-z]+)\}\{(?P<decl_expr>.+?)\}
    |
    \\ensuremath\{(?P<ensure>.+?)\}
    """,
    re.DOTALL | re.VERBOSE
)

def normalize_latex(expr):
    """
    Math-specific normalization without adding extra spaces around operators.
    Args:
        expr (str): The LaTeX expression to normalize.

    Returns:
        str: The normalized LaTeX expression.
    """
    expr = re.sub(
        r'\\operatorname\*?\{([^{}]+)\}',
        lambda m: '\\' + m.group(1).replace(' ', ''),
        expr
    )
    # Remove any spaces immediately following one or more backslashes.
    expr = re.sub(r'(\\+)\s+', r'\1', expr)
    # Remove \text{...} or \mbox{...} blocks entirely.
    expr = re.sub(r'\\(text|mbox)\s*\{.*?\}', '', expr)
    # Remove or normalize spaces around certain operators
    operators = r'([=+\-*/^<>:;])'
    expr = re.sub(rf'\s*{operators}\s*', r'\1', expr)
    #  Collapse all other internal whitespace to a single space and strip leading/trailing space.
    expr = ' '.join(expr.split()).strip()

    return expr

def replace_latex_inline(text: str):
    """
    Replace LaTeX expressions in text with <<MATH: ... >> tags after normalizing.

    Args:
        text (str): The text to replace LaTeX expressions in.

    Returns:
        str: The full text with LaTeX expressions normalized and replaced with <<MATH: ... >> tags.
    
    Note: 
        This function is used to extract LaTeX expressions from text and replace them inline with <<MATH: ... >> tags after normalizing.
    """
    new_text = []
    last_end = 0

    for match in latex_pattern.finditer(text):
        start, end = match.span()
        new_text.append(text[last_end:start])

        expr_text = None
        for group in ['dcontent', 'env_content', 'inline', 'brack',
                      'xtd_content', 'ensure', 'decl_expr']:
            if match.group(group):
                expr_text = match.group(group)
                break

        if expr_text:
            expr_text = normalize_latex(expr_text)
            inline_math = f"<<MATH: {expr_text} >>"
            new_text.append(inline_math)
        last_end = end

    new_text.append(text[last_end:])
    return ''.join(new_text)