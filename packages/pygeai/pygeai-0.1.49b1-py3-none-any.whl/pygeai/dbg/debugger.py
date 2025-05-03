import logging
import sys

from pygeai.cli.geai import main as geai


class Debugger:
    def __init__(self):
        self.setup_logging()
        logging.getLogger('geai').info("GEAI debugger started.")

    def setup_logging(self):
        logger = logging.getLogger('geai')
        logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    def run(self):
        sys.exit(geai())


if __name__ == "__main__":
    dbg = Debugger()
    dbg.run()
