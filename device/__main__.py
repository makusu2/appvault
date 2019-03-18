"""
Main function for appvault device.
"""


from .watcher import Watcher


if __name__ == "__main__":
    Watcher().keep_checking()
