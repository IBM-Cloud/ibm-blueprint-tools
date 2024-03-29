# (C) Copyright IBM Corp. 2022.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import yamale
import os
import sys
import pkgutil

from typing import Tuple

from pathlib import Path
from typing import Dict
from blueprint.validate.custom.settings import Settings

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

from yamale.validators import DefaultValidators

from blueprint.lib.logger import logr
import logging
logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

def _get_lc_dict_helper(data: CommentedMap, dict_key_line: Dict[str, int], parentkey: str = "") -> Dict[str, int]:
    """
    Recursive helper function to fetch the line infos of each keys in the config yaml file.

    Built to be called inside of `_get_lc_dict`.
    """
    sep = "."  # Don't modify, it is to match the "keys" return in the errors of the yamale lib.
    keys_indexes = None

    try:
        if len(data) > 0:
            keys_indexes = range(len(data))
    except TypeError:
        pass
    try:
        keys = data.keys()
        keys_indexes = keys
    except AttributeError:
        pass

    if keys_indexes is None:
        return dict_key_line  # return condition from recursion

    for key in keys_indexes:
        if parentkey != "":
            keyref = parentkey + sep + str(key)
        else:
            keyref = str(key)
        try:
            lnum = data.lc.data[key][0] + 1
            if keyref in dict_key_line:
                eprint(
                    f"WARNING : key '{keyref}' is NOT UNIQUE, at lines {dict_key_line[keyref]:>4} and {lnum:>4}."
                    f" (overwriting)."
                )
            dict_key_line[keyref] = lnum
            # print(f"line {lnum:<3} : {keyref}")
            _get_lc_dict_helper(data[key], dict_key_line, keyref)  # recursion
        except AttributeError:
            pass

    return dict_key_line


def _get_lc_dict(path: Path) -> Dict[str, int]:
    """
    Helper function to trace back the line number in the yaml file for each keys.

    Built to be called inside of `validate`.

    Parameters
    ----------
    path : Path
        Path to the config yaml file (not the schema).

    Returns
    -------
    Dict[str, int]
        Maps the keys to their line number, the line counter (lc).
        This dictionary is only 1 level and the keys corresponds to the ones report by the yamale lib.
    """
    dict_key_line: Dict[str, int] = {}
    with YAML(typ="rt") as yaml:
        for data in yaml.load_all(path):
            dict_key_line = _get_lc_dict_helper(data, dict_key_line)
    return dict_key_line



class SchemaValidator():
    def __init__(self, filename):
        
        logr.debug("Loading blueprint yaml schema file")
        self.schema = os.path.join(os.path.dirname(__file__), '../schema/schema.yaml')
        self.filename = filename 

    def validate(self):
        """
        Validates the config yaml file according to the schema yaml file.

        Will be silent if good and will exit the program if there is an error,
        and will output an detailed error message to fix the config file.
        """
        validators = DefaultValidators.copy()  # This is a dictionary
        validators[Settings.tag]=Settings
        # Create a schema object
        schema = yamale.make_schema(path=self.schema, parser="PyYAML",validators=validators)

        # Create a Data object
        config = yamale.make_data(path=self.filename, parser="ruamel")

        try:
            # Validate data against the schema. Throws a ValueError if data is invalid.
            yamale.validate(schema, config)
            ret_str = "\nBlueprint yaml schema validation success!👍 \n\n"
            logr.info("Blueprint yaml schema validation success!")
            return (ret_str, None)
        
        except yamale.YamaleError as e:
            errmsg = "Blueprint yaml schema validation failed!\n"

            lc = _get_lc_dict(self.filename)
            for result in e.results:
                title1 = "Schema"
                title2 = "Config"
                sep = f"{'-'*40}\n"
                errmsg += f"{title1:<10} : {result.schema}\n{title2:<10} : {result.data}\n{sep}"
                for error in result.errors:
                    keyerr = error.split(":", 1)
                    keypath = keyerr[0]
                    err = keyerr[1]
                    l_num = lc.get(keypath, "?")
                    errmsg += f"* line {l_num:>4}:  {keypath:<40} : {err}\n"
                errmsg += f"{sep}"
                
            logr.error(errmsg)
            return (None, errmsg)



