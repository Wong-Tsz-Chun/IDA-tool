import os

def generate_tree(startpath, indent='  '):
    print(f'\nProject Structure of: {os.path.basename(startpath)}\n')
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent_str = indent * level
        print(f'{indent_str}{os.path.basename(root)}/')
        sub_indent = indent_str + indent
        for f in files:
            if not f.startswith('.') and not '__pycache__' in root:
                print(f'{sub_indent}{f}')

# Use the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
generate_tree(current_dir)