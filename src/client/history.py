"""
Client history object definition
"""
class ClientHistory:

    def __init__(self):
        self.username = None
        self.start = None
        self.end = None
        self.products = None
        self.history = None

    def compile(self, client):
        "Leverages the provided client to compile the history."

    def save(self, path:  str='../../history/'):
        raise NotImplementedError

    @classmethod
    def load(path):
        return NotImplementedError

    def _encrypt(self):
        "Return the encrypted self bitstream."


