class NoBlockFoundError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class BlockDataError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)