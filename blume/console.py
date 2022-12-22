
import readline
import rlcompleter
import sys

import code
import asyncio

from blume import magic, farm


class Console(magic.Ball):
    """ Prompt for input """

    def __init__(self, **kwargs):

        super().__init__()

        if kwargs:
            self.__dict__.update(kwargs)

    async def start(self):


        # kludge together a namespace for the console and completer
        names = {}
        names.update(self.__dict__)
        names.update(globals())
        names.update(locals())

        completer = rlcompleter.Completer(names)
        readline.set_completer(completer.complete)
        self.console = code.InteractiveConsole(names)

        # incantation to make tab completion work
        readline.parse_and_bind("tab: complete")

    async def run(self):

        loop = asyncio.get_running_loop()

        await magic.sleep(0.5)

        banner = """
********************************
Welcome to the magic console.
Your wish is my command!
********************************
"""

        print(banner)

        while True:

            key = await loop.run_in_executor(
                None, input, '>>> ')

            # Single character inputs => put them into the
            # Magic RoundAbout
            if len(key.strip()) == 1:
                char = key.strip()
                await self.put(char, char)
            else:
                self.console.push(key)


        
            

if __name__ == '__main__':

    curio.run(run())
