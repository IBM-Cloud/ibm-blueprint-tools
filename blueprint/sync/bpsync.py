# (C) Copyright IBM Corp. 2022.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import yaml
from typing import List

from os.path import exists as file_exists
import giturlparse

from blueprint.schema import blueprint
from blueprint.schema import module
from blueprint.schema import param
from blueprint.schema import source as src

from blueprint.circuit import bus

from blueprint.lib import git
from blueprint.lib import type_helper
from blueprint.lib import bfile

from python_terraform import *

import subprocess

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

class BlueprintMorphius:

    def __init__(self, 
                    name: str                       = "__init__", 
                    description: str                = None, 
                    inputs: List[param.Input]       = None, 
                    outputs: List[param.Output]     = None, 
                    settings: List[param.Setting]   = None,
                    modules: List[module.Module]    = None ):
        self.name = name
        self.description = description
        self.inputs = inputs
        self.outputs = outputs
        self.settings = settings
        self.modules = modules

    @classmethod
    def from_yaml_file(cls, filename):
        if not file_exists(filename):
            raise ValueError('Blueprint manifest file does not exist')

        yaml_data = bfile.FileHelper.load(filename)        

        bp = BlueprintMorphius.from_yaml_data(yaml_data)
        return cls(name=bp.name, description=bp.description, inputs=bp.inputs, 
                    outputs=bp.outputs, settings=bp.settings, modules=bp.modules)

    @classmethod
    def from_yaml_str(cls, yaml_str):
        yaml_data = yaml.safe_load(yaml_str)
        bp = BlueprintMorphius.from_yaml_data(yaml_data)
        return cls(name=bp.name, description=bp.description, inputs=bp.inputs, 
                    outputs=bp.outputs, settings=bp.settings, modules=bp.modules)

    @classmethod
    def from_yaml_data(cls, yaml_data):
        bp_name = yaml_data['name']
        try:
            description = yaml_data['description']
        except KeyError:
            description = None
        
        inputs=[]
        try:
            params = yaml_data['inputs']
            for p in params:
                inputs.append(param.Input.from_yaml(p))
        except KeyError:
            inputs=[]

        outputs=[]
        try:
            params = yaml_data['outputs']
            for p in params:
                outputs.append(param.Output.from_yaml(p))
        except KeyError:
            outputs=[]

        settings=[]
        try:
            params = yaml_data['settings']
            for p in params:
                settings.append(param.Setting.from_yaml(p))
        except KeyError:
            settings=[]

        modules=[]
        try:
            mods = yaml_data['modules']
            for mod in mods:
                modules.append(module.Module.from_yaml(mod))
        except KeyError:
            modules=[]

        try:
            git_sources = yaml_data['git_sources']
            for s in git_sources:
                git_url = s['git_repo_url']
                try:
                    git_branch = s['git_branch']
                except KeyError:
                    git_branch = None
                try:
                    git_token = s['git_token']
                except KeyError:
                    git_token = None

                p = giturlparse.parse(git_url)
                name = p.name
                module_type = 'terraform'
                git_source = src.GitSource(git_url, git_branch, git_token)
                source = src.TemplateSource('github', git_source)

                modules.append(module.Module(name, type=module_type, source=source))

        except (KeyError, UnboundLocalError, TypeError) as e:
            logr.debug('Attribute error while reading & initializing modules from git_sources' + str(e))

        return cls(name=bp_name, description=description, inputs=inputs, 
                    outputs=outputs, settings=settings, modules=modules)

    def sync_blueprint(self, working_dir, annotate=False) -> blueprint.Blueprint:
        cwd = os.getcwd()

        tic_path = os.getenv('TERRAFORM_CONFIG_INSPECT_PATH')
        if tic_path == None:
            err_msg = 'Could not find terraform-config-inspect.  Install and set install path in environment $TERRAFORM_CONFIG_INSPECT_PATH'
            logr.error(err_msg)
            raise ValueError(err_msg)

        if not os.path.exists(working_dir):
            logr.info('Working directory does not exists.  Creating the required working director : ' + str(os.path.abspath(working_dir)))
            os.makedirs(working_dir, exist_ok=True)
        working_dir = os.path.abspath(working_dir)
        os.chdir(working_dir)

        bp = blueprint.Blueprint(name=self.name, description=self.description, 
                                    inputs=self.inputs,
                                    outputs=self.outputs,
                                    settings=self.settings,
                                    modules=self.modules)
        
        if bp.modules != None and len(bp.modules) > 0:
            for mod in bp.modules:
                # if not 'git' in mod.source:
                #     print(str(mod))
                #     logr.warn('Git URL source is not found in  ' + mod.name)
                #     continue
                git_url = mod.source.git.git_repo_url
                if hasattr(mod.source.git, 'git_token'):
                    git_token = mod.source.git.git_token
                else:
                    git_token = None
                
                downloader = git.GitDownloadTemplate(git_url, git_token, mod.name)
                wd = downloader.get_working_dir()

                result = subprocess.run([os.path.join(tic_path, 'terraform-config-inspect'), wd, '--json'], stdout=subprocess.PIPE)
                config_json = result.stdout
                config_json_data = yaml.safe_load(config_json)

                if config_json != None:
                    config_json_data = yaml.safe_load(config_json)

                    #==============================
                    # Processing input variables
                    config_input_vars = list(config_json_data['variables'].keys())
                    logr.info('Processing inputs: ' + str(config_input_vars))
                    existing_input_vars = mod.list_input_param_names()

                    for key in config_input_vars:

                        config_value = config_json_data['variables'][key]
                        if 'type' in config_value.keys():
                            type=config_value['type']
                        else:
                            type=None
                        if 'description' in config_value.keys():
                            description=config_value['description']
                        else:
                            description=''
                        if 'default' in config_value.keys():
                            val=config_value['default']
                        else:
                            val=None
                        if type == None:
                            if val != None:
                                type = type_helper.val_type(val)
                                if type == 'str' and (val.startswith('$blueprint') or val.startswith('$module')):
                                    type = None
                            if type == 'unknown':
                                type = None

                        # If key already present in the 'mod', then update parameter
                        if key in existing_input_vars:
                            type2 = mod.get_input_attr(key, "type")
                            description2 = mod.get_input_attr(key, "description")
                            val2 = mod.get_input_attr(key, "value")
                            comment2 = 'NOTES: update param '
                            is_updated = False
                            if type != type2:
                                comment2 += f'type({type2} --> {type}) '
                                is_updated = True
                            if description != description2:
                                comment2 += f'description({description2} --> {description}) '
                                is_updated = True
                            if val != val2 and not (val2.startswith('$blueprint.') or val2.startswith('$module.')):
                                comment2 += f'value({val2} --> {val})'
                                is_updated = True
                            if is_updated == True and type == None:
                                if val != None:
                                    type = type_helper.val_type(val)
                                    if type == 'str' and (val.startswith('$blueprint') or val.startswith('$module')):
                                        type = None
                                if type == 'unknown':
                                    type = None

                            if is_updated:
                                p = param.Input(key, type=type, description=description, value=val, comment=comment2 if annotate else None)
                                mod.update_input(p)
                        else:
                            p = param.Input(key, type=type, description=description, value=val, comment='NOTES: add param' if annotate else None)
                            mod.inputs.append(p)

                        # if p.value == None and key not in bp.list_input_param_names():
                        #     bp_input = param.Input(key, type=type, description=description, value=val, comment='NOTES: add param' if annotate else None)
                        #     bp.add_input(bp_input)
                        #     bp_bus = bus.WireBus(bp, mod)
                        #     bp_bus.add_wire(bp_input.name, p.name)

                    config_input_vars = list(config_json_data['variables'].keys())
                    # existing_input_vars = mod.list_input_param_names()
                    for key in existing_input_vars:
                        if key not in config_input_vars and annotate:
                            mod.set_input_attr(key, 'comment', 'TODO: delete param')
                    
                    #==============================
                    # Processing output variables
                    config_output_vars = list(config_json_data['outputs'].keys())
                    logr.info('Processing outputs: ' + str(config_output_vars))
                    existing_output_vars = mod.list_output_param_names()
                    for key in config_output_vars:

                        value = config_json_data['outputs'][key]
                        if 'description' in value.keys():
                            description=value['description']
                        else:
                            description=''
                        # If key already present in the 'mod', then skip
                        if key in existing_output_vars:
                            description2 = mod.get_output_attr(key, "description")
                            comment2 = 'NOTES: update param '
                            is_updated = False
                            if description != description2:
                                comment2 += f'description({description} --> {description2})  '
                                is_updated = True
                            if is_updated:
                                p = param.Output(key, description=description, comment=comment2 if annotate else None)
                                mod.update_input(p)
                        else:
                            p = param.Output(key, description=description, comment='NOTES: add param' if annotate else None)
                            mod.outputs.append(p)

                        mod_ref = bp.module_output_ref(mod.name, p.name)
                        is_p_linked = False
                        for op in bp.outputs:
                            if hasattr(op, 'value') and mod_ref == op.value:
                                is_p_linked = True
                                break

                        if not is_p_linked and key not in bp.list_output_param_names():
                            bp_output = param.Output(key, description=description, comment='NOTES: add param' if annotate else None)
                            bp.add_output(bp_output)
                            bp_bus = bus.WireBus(mod, bp)
                            bp_bus.add_wire(p.name, bp_output.name)

                    config_output_vars = list(config_json_data['outputs'].keys())
                    # existing_output_vars = mod.list_input_param_names()
                    for key in existing_output_vars:
                        if key not in config_output_vars and annotate:
                            mod.set_input_attr(key, 'comment', 'TODO: delete param')

        os.chdir(cwd)
        return bp

