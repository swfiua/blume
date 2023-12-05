
import code
import asyncio
import sys
from pathlib import Path

if sys.platform != 'emscripten':
    import readline
    import rlcompleter

    InteractiveConsole = code.InteractiveConsole
else:
    from pyodide.console import Console as InteractiveConsole
    readline = False


from blume import magic


class Console(magic.Ball):
    """ Prompt for input """

    def __init__(self, **kwargs):

        super().__init__()

        self.prompt = '>>> '

        self.history = Path('~/.blume_history').expanduser()
        if kwargs:
            self.__dict__.update(kwargs)

    def complete(self, text):

        completions, index = self.console.complete(text)
        if len(completions) == 1:
            return completions[0]

        print(' '.join(completions))
        return None
        

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
            readline.set_auto_history(True)
            if self.history.exists():
                readline.read_history_file(self.history)

        if sys.platform != 'emscripten':
            
            self.stdin_relay = magic.spawn(self.relay_stdin())


    async def relay_stdin(self, txt=None):
        """ Put stdin into a queue 

        This is useful(?) since code below can just wait on that
        queue and not worry about actual stdin eg on a pyodide web page.

        """

        loop = asyncio.get_running_loop()

        while True:
            key = await loop.run_in_executor(
                None, input, txt or self.prompt)

            await self.put(key, 'stdin')
            

    async def run(self):


        banner = """
********************************
Welcome to the magic console.
Your wish is my command!
********************************
"""

        print(banner)

        # print(self.prompt, end='')
        while True:
            key = await self.get('stdin')

            # Single character inputs => put them into the
            # Magic RoundAbout
            if len(key.strip()) == 1 and not self.console.buffer:
                char = key.strip()
                await self.put(char, char)
            else:
                try:
                    result = self.console.push(key)
                    if sys.platform == 'emscripten':
                        """ emscriptem returns a promise 
                            that needs to be awaited 

                        TODO: unravel how it deals with incomplete 
                              lines of input.
                        """
                        result = await result
                        if result is not None: print(result)
                        #print(self.prompt, end='')
                    else:
                        if result:
                            [print(x) for x in self.console.buffer]
                        else:
                            pass
                            #print()
                            #print(self.prompt, end='')
                    readline and readline.write_history_file(self.history)

                except Exception as e:
                    print("exception")
                    print(e)
                    result = e
                #await self.put(result, 'stdout')



if __name__ == '__main__':

    curio.run(run())
