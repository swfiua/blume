
import code
import asyncio
import sys

print('PLATFORM' * 3)
print(sys.platform)
if sys.platform != 'emscripten':
    import readline
    import rlcompleter

    InteractiveConsole = code.InteractiveConsole
else:
    from pyodide.console import Console as InteractiveConsole
    readline = False


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

        self.console = InteractiveConsole(names)

        # incantation to make tab completion work 
        if readline:
            completer = rlcompleter.Completer(names)
            readline.set_completer(completer.complete)
            readline.parse_and_bind("tab: complete")

        print("starting relay of stdin")
        if sys.platform != 'emscripten':
            
            self.stdin_relay = magic.spawn(self.relay_stdin())

        print("started relay of stdin")


    async def relay_stdin(self, txt='>>> '):
        """ Put stdin into a queue """

        loop = asyncio.get_running_loop()
        while True:
            key = await loop.run_in_executor(
                None, input, '>>> ')

            await self.put(key, 'stdin')
            

    async def run(self):


        banner = """
********************************
Welcome to the magic console.
Your wish is my command!
********************************
"""

        print(banner)

        while True:

            key = await self.get('stdin')

            # Single character inputs => put them into the
            # Magic RoundAbout
            if len(key.strip()) == 1:
                char = key.strip()
                await self.put(char, char)
            else:
                self.console.push(key)


        
            

if __name__ == '__main__':

    curio.run(run())
