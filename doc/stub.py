"""
create a stub file that just extracts the doc from the module.
"""
import sys
module = sys.argv[1]

ss = """
=======
Straight from the code for ${module}
=======

..automodule: blume.${module}::
    :members:
"""

with open(f'{module}.rst', 'w') as f:
    f.write(ss % dict(module=module))
