import re

file_path = '/Users/mark/Coding/Bachelors/My_Thesis/chapters/results.tex'

with open(file_path, 'r') as f:
    content = f.read()

# We want to find:
# \end{figure}
# 
# \begin{table}[H]
# \centering
# \begin{tabular}...
# ...
# \end{tabular}
# \caption{...}
# \label{...}
# \end{table}

# And replace it with:
# \vspace{1.5em}
# \begin{tabular}...
# ...
# \end{tabular}
# \captionof{table}{...}
# \label{...}
# \end{figure}

pattern = re.compile(
    r'\\end\{figure\}\s*\\begin\{table\}\[H\]\s*\\centering\s*(\\begin\{tabular\}.*?\\end\{tabular\})\s*\\caption\{(.*?)\}\s*\\label\{(.*?)\}\s*\\end\{table\}',
    re.DOTALL
)

def repl(match):
    tabular_content = match.group(1)
    caption_text = match.group(2)
    label_text = match.group(3)
    
    return f"""
    \\vspace{{1.5em}}
    
    {tabular_content}
    \\captionof{{table}}{{{caption_text}}}
    \\label{{{label_text}}}
\\end{{figure}}"""

new_content = pattern.sub(repl, content)

# Remove the \clearpage lines we added previously
new_content = new_content.replace('\\end{table}\n\n\\clearpage', '\\end{table}')
new_content = new_content.replace('\\end{figure}\n\n\\clearpage', '\\end{figure}')
# The clearpage might be slightly different now because we already replaced \end{table} above.
# Let's just remove \clearpage that are standing alone between the pairs.

new_content = re.sub(r'\\label\{(tab:.*?)\}\n\\end\{figure\}\n\n\\clearpage', r'\\label{\1}\n\\end{figure}', new_content)

with open(file_path, 'w') as f:
    f.write(new_content)

print("Done replacing.")
