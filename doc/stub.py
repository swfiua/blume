"""
create a stub file that just extracts the doc from the module.
"""
import sys
module, title = sys.argv[1:3]
print(module)
print(title)

ss = """
=======
%s
=======


.. automodule:: blume.%s
    :members:


"""

with open(f'{module}.rst', 'w') as f:
    f.write(ss % (title, module))
