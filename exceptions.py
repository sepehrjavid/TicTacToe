class NotEmptySpotException(Exception):
    def __init__(self):
        self.message = "This field is not empty, try again...\n"
