import argparse
from sys import exit


class CLI:

    @classmethod
    def get_parser(cls, logger=None):
        """setup a CLI

        Args:
            logger: logger is None, then msg will be print on the standout

        Returns:
            return cli handler

        """
        try:
            parser = argparse.ArgumentParser(
                description="Demo create AWS resources using python SDK 'create' mode to is create AWS resources. "
                            "'destroy' mode is to clean up all resources ")
            parser.add_argument("--mode", choices=['create', 'destroy'], help="action the script performs.")

            args = parser.parse_args()
            return args

        except Exception as err:
            logger.critical(f"Error creating/parsing arguments:\n{str(err)}")
            exit(99)


def get_parser():
    return CLI.get_parser()
