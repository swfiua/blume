"""
create a stub file that just extracts the doc from the module.
"""
import sys
module = sys.argv[1]

ss = """
..automodule: blume.%s::
    :members:
"""

with open(f'{module}.rst', 'w') as f:
    f.write(ss % module)
