class ExitREPL(Exception):
    def __init__(self, code=0):
        self.code = code
        super().__init__(f"Exiting with code {code}")