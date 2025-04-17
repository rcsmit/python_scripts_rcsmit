text = """
# Paste the text here
"""

lines = text.splitlines()
unique_lines = list(set(lines))
cleaned_text = "\n".join(unique_lines)

print(cleaned_text)