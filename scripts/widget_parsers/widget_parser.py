import argparse
from glob import glob
from importlib import import_module
import os
import sys

EIGHTSPC = " " * 8
FOURSPC = " " * 4

def build_raw_classes(parser, repo_folder):
    classes = parser.widget_list
    build_folder = os.path.join(repo_folder,
                                f"external_widgets{os.path.sep}",
                                parser.widget_code
                                )
    os.makedirs(build_folder, exist_ok=True)
    raw_file = os.path.join(build_folder,
                            f"raw_widgets_{parser.widget_code}.py"
                            )
    with open(raw_file, "w") as rfile:
        rfile.write("from uuid import uuid4\n\n")
        rfile.write("from decorators.decorators import (function_wrapper, event_wrapper, init_wrapper)\n")
        for widget_class in classes:
            widget_info = parser._classes[widget_class]
            rfile.write(f"\n\nclass {widget_class}:\n")
            rfile.write(f"{FOURSPC}def __init__(self):\n")
            rfile.write(f"{EIGHTSPC}self._unique_id = str(uuid4())\n")
            rfile.write(f"{EIGHTSPC}self._event_param_qty = " + "{\n")
            for jsevent in sorted(widget_info["events"].keys()):
                jsevent_info = widget_info["events"][jsevent]
                rfile.write(f'{EIGHTSPC}{FOURSPC}"{jsevent}": {jsevent_info["argslen"]},\n')
            rfile.write(f"{EIGHTSPC}" + "}\n")
            rfile.write(f"\n{FOURSPC}@init_wrapper\n")
            rfile.write(f"{FOURSPC}def init{widget_class}(self, config):\n")
            rfile.write(f"{EIGHTSPC}pass\n")
            for jsfunction in widget_info["functions"]:
                rfile.write(f"\n{FOURSPC}@function_wrapper")
                rfile.write(f"\n{FOURSPC}def {jsfunction['name']}(self")
                if jsfunction["params"]:
                    rfile.write(", " + (", ".join(jsfunction["params"])))
                rfile.write("):\n")
                rfile.write(f"{EIGHTSPC}pass\n")
            for jsevent in sorted(widget_info["events"].keys()):
                jsevent_info = widget_info["events"][jsevent]
                rfile.write(f"\n{FOURSPC}@event_wrapper")
                rfile.write(f"\n{FOURSPC}def {jsevent}(self")
                rfile.write(f", callable, ret_widget_values=[], block_signal = False):\n")
                rfile.write(f'{EIGHTSPC}"""JS_ARGS: {jsevent_info["argstr"]}"""\n')
                rfile.write(f"{EIGHTSPC}pass\n")
        

def run_parsers(repo_folder):
    folder = os.path.join(
        os.path.dirname(__file__),
         f"parsers{os.path.sep}*.py"
    )
    files = glob(folder)
    for parse_file in files:
        file_only = parse_file.split(os.path.sep)[-1]
        sys.path.append(os.path.dirname(parse_file))
        parsemod = import_module(file_only.replace(".py", ""))
        parser = parsemod.parser()
        parser.build_widget_info()
        build_raw_classes(parser, repo_folder)


if __name__ == "__main__":
    #get and parse arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--pywrm_project_path',
        help='path to pywrm project',
        default= os.path.dirname(__file__)
    )
    args = arg_parser.parse_args()
    run_parsers(args.pywrm_project_path)