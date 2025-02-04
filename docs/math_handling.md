# Mathematical Content Handling

## LaTeX Processing Pipeline

1. **Pattern Matching**
    - Identify LaTeX expressions in text
    - Extract LaTeX expressions from text

2. **Normalization**
    - Normalize LaTeX expressions
        - Remove extra spaces around operators
        - Removes text blocks inside math environments
        - Simplifies operator declarations

3. **Replacement**
    - Replace LaTeX expressions with <<MATH: ... >> tags
        - Normalized LaTeX expressions are replaced inline with <<MATH: ... >> tags
    - Original positions preserved in metadata

## Usage Guide

### Processing Math Documents
1. Upload PDF/text files containing LaTeX
2. System automatically detects and processes formulas
3. Query using natural language or formula fragments

### Example Queries
1. What is formula for Bayes' theorem?
2. What is the formula for Combinations?
3. Rolling a die is a random experiment. An outcome can be any number from 1
to 6. Sample space = \{1, 2, 3, 4, 5, 6\}. What are some possible events?
4. What is the integral of $e^{-x^2}$


