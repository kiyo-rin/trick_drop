with open("app.py", "r") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if line.startswith("import streamlit.components.v1 as components"):
        skip = True
    
    if skip and line.startswith(")"):
        skip = False
        continue
    
    if not skip:
        new_lines.append(line)

with open("app.py", "w") as f:
    f.writelines(new_lines)

with open("patch.py", "r") as f:
    patch_code = f.read()

with open("app.py", "r") as f:
    content = f.read()

# Insert patch right after st.set_page_config
target = 'st.set_page_config(page_title="TRICK DROP", page_icon="⚡️", layout="wide")'
content = content.replace(target, target + "\n\n" + patch_code)

with open("app.py", "w") as f:
    f.write(content)

print("done")
