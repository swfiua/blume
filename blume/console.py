
import readline
import sys

import code

from blume import magic, farm

import curio
from curio.file import aopen, AsyncFile

async def run():

    xx = AsyncFile(sys.stdin)

    console = code.InteractiveConsole(locals())

    while True:

        line = await xx.readline()
        try:
            console.runcode(line)
            #print(eval(line))
        except Exception as e:
            print(e)
    

if __name__ == '__main__':

    curio.run(run())
