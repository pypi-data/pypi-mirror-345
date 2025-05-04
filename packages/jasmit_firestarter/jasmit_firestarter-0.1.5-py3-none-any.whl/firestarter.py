'''
Fire-Starter
'''

from std_app import StdApp
from traceback import print_exc
from argparse import ArgumentParser


class FireStarter(StdApp):
    def __init__(self):
        super().__init__("Fire-Starter")


    def set_cmdline_params(self):
        parser = ArgumentParser(description="TROLoadBank")
        parser.add_argument(
            "-e",
            "--environment",
            required=False,
            help="Environment - devl, test or prod",
        )
        parser.add_argument(
            "-c",
            "--cfgfile",
            required=False,
            default="etc/firestarter.cfg",
            help="Name of the configuration file to use",
        )
        args = parser.parse_args()
        return vars(args)

    def say_hello(self):
        print("Hello from Fire-Starter!")



 #  =============================================================================
if __name__ == "__main__":
    try:
        this_app = FireStarter()
        this_app.say_hello()
    except Exception as e:
        print(f"Following uncaught exception occured. {e}")
        print_exc()
