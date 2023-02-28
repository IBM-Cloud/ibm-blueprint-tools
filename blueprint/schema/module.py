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

import yaml
import sys
from typing import List, Union

from blueprint.schema import param
from blueprint.schema import source as src
from blueprint.schema import injector

from blueprint.validate import module_validator
from blueprint.lib import event

from blueprint.lib.logger import logr
# import logging
# logr = logging.getLogger(__name__)

def eprint(*args, **kwargs):
    logr.error(*args)
    print(*args, file=sys.stderr, **kwargs)

#========================================================================
TerraformType = "terraform"

class Module(dict):
    def __init__(self, 
                    name: str                       = "__init__", 
                    type: str                       = TerraformType, 
                    layer: str                      = None, 
                    source: src.TemplateSource      = {}, 
                    inputs: List[param.Input]       = None, 
                    outputs: List[param.Output]     = None, 
                    settings: List[param.Setting]   = None,
                    injectors: List[injector.Injector]       = None,
                    comment: str                    = None):
        """Module schema.

        :param name: Name of the module
        :param type: Type of module (default is `terraform`)
        :param layer: Layer of module (default is None)
        :param source: Source of module - Git source or Catalog source
        :param inputs: List of input parameters (type param.Input)
        :param outputs: List of output parameters (type param.Output)
        :param settings: List of environment settings (type param.Setting)
        """
        self.name = name
        self.module_type = type
        self.layer = layer
        self.source = source
        self.inputs = []
        self.outputs = []
        self.settings = []
        self.injectors = []
        self.set_inputs(inputs)
        self.set_outputs(outputs)
        self.set_settings(settings)
        self.injectors = injectors
        self.comment = comment

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.name = "__init__"

    def __str__(self):
        txt = "Modules("
        txt += "name:" + str(self.name if hasattr(self, 'name') else 'None') + ", "
        txt += "type:" + str(self.module_type if hasattr(self, 'module_type') else 'None') + ", "
        txt += "layer:" + str(self.layer if hasattr(self, 'layer') else 'None') + ", "
        txt += "inputs:" + str(self.inputs if hasattr(self, 'inputs') else 'None') + ", "
        txt += "outputs:" + str(self.outputs if hasattr(self, 'outputs') else 'None') + ", "
        txt += "settings:" + str(self.settings if hasattr(self, 'settings') else 'None') + ", "
        txt += "injectors:" + str(self.injectors if hasattr(self, 'injectors') else 'None') + ", "
        txt += "source:" + str(self.source if hasattr(self, 'source') else 'None')
        txt += ")"
        return txt

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if other == None:
            return False

        self_name = "" if self.name == None else self.name
        self_module_type = "" if not hasattr(self, 'module_type') or self.module_type == None else self.module_type
        self_layer = "" if not hasattr(self, 'layer') or self.layer == None else self.layer
        self_source = "" if not hasattr(self, 'source') or self.source == None else str(self.source)
        self_inputs = "" if not hasattr(self, 'inputs') or self.inputs == None else str(self.inputs)
        self_outputs = "" if not hasattr(self, 'outputs') or self.outputs == None else str(self.outputs)
        self_settings = "" if not hasattr(self, 'settings') or self.settings == None else str(self.settings)
        self_injectors = "" if not hasattr(self, 'injectors') or self.injectors == None else str(self.injectors)

        other_name = "" if other.name == None else other.name
        other_module_type = "" if not hasattr(other, 'module_type') or other.module_type == None else other.module_type
        other_layer = "" if not hasattr(other, 'layer') or other.layer == None else other.layer
        other_source = "" if not hasattr(other, 'source') or other.source == None else str(other.source)
        other_inputs = "" if not hasattr(other, 'inputs') or other.inputs == None else str(other.inputs)
        other_outputs = "" if not hasattr(other, 'outputs') or other.outputs == None else str(other.outputs)
        other_settings = "" if not hasattr(other, 'settings') or other.settings == None else str(other.settings)
        other_injectors = "" if not hasattr(other, 'injectors') or other.injectors == None else str(other.injectors)

        return (self_name == other_name) and (self_module_type == other_module_type) and (self_layer == other_layer) \
            and (self_source == other_source) \
            and (self_inputs == other_inputs) and (self_outputs == other_outputs) \
            and (self_settings == other_settings) and (self_injectors == other_injectors)

    def __hash__(self):
        self_name = "" if self.name == None else self.name
        self_module_type = "" if not hasattr(self, 'module_type') or self.module_type == None else self.module_type
        self_layer = "" if not hasattr(self, 'layer') or self.layer == None else self.layer
        self_source = "" if not hasattr(self, 'source') or self.source == None else self.source
        self_inputs = "" if not hasattr(self, 'inputs') or self.inputs == None else str(self.inputs)
        self_outputs = "" if not hasattr(self, 'outputs') or self.outputs == None else str(self.outputs)
        self_settings = "" if not hasattr(self, 'settings') or self.settings == None else str(self.settings)
        self_injectors = "" if not hasattr(self, 'injectors') or self.injectors == None else str(self.injectors)

        return hash((self_name, self_module_type, self_layer, self_source, self_inputs, self_outputs, self_settings, self.injectors))

    def remove_null_entries(self):
        if hasattr(self, 'name') and self.name == None:
            del self.name
        if hasattr(self, 'module_type') and self.module_type == None:
            del self.module_type
        if hasattr(self, 'layer') and self.layer == None:
            del self.layer
        if hasattr(self, 'source') and self.source == None:
            del self.source

        if hasattr(self, 'inputs'):
            if self.inputs == None or (self.inputs != None and len(self.inputs) == 0):
                del self.inputs
            else:
                for p in self.inputs:
                    p.remove_null_entries()

        if hasattr(self, 'outputs'):
            if self.outputs == None or (self.outputs != None and len(self.outputs) == 0):
                del self.outputs
            else:
                for p in self.outputs:
                    p.remove_null_entries()

        if hasattr(self, 'settings'):
            if self.settings == None or (self.settings != None and len(self.settings) == 0):
                del self.settings
            else:
                for p in self.settings:
                    p.remove_null_entries()

        if hasattr(self, 'injectors'):
            if self.injectors == None or (self.injectors != None and len(self.injectors) == 0):
                del self.injectors
            else:
                for i in self.injectors:
                    i.remove_null_entries()

        if hasattr(self, 'comment') and self.comment == None:
            del self.comment
    
    def to_yaml(self):
        # yaml.encoding = None
        errors = self.validate()
        # eprint(errors)
        return (yaml.dump(self, sort_keys=False), errors)

    @classmethod
    def from_yaml(cls, yaml_data):
        
        if isinstance(yaml_data, Module):
            return yaml_data

        name = yaml_data['name']
        try:
            module_type = yaml_data['module_type']
        except KeyError:
            module_type = None
        try:
            layer = yaml_data['layer']
        except KeyError:
            layer = None
        try:
            source = src.TemplateSource.from_yaml(yaml_data['source'])
        except KeyError:
            source = None
        try:
            inputs = []
            for p in yaml_data['inputs']:
                inputs.append(param.Input.from_yaml(p))
        except (KeyError, UnboundLocalError, TypeError):
            inputs = None
        try:
            outputs = []
            for p in yaml_data['outputs']:
                outputs.append(param.Output.from_yaml(p))
        except (KeyError, UnboundLocalError, TypeError):
            outputs = None
        try:
            settings = []
            for p in yaml_data['settings']:
                settings.append(param.Setting.from_yaml(p))
        except (KeyError, UnboundLocalError, TypeError):
            settings = None

        try:
            injectors = []
            for i in yaml_data['injectors']:
                injectors.append(injector.Injector.from_yaml(i))
        except (KeyError, UnboundLocalError, TypeError):
            injectors = None


        return cls(name, module_type, layer, source, inputs, outputs, settings, injectors)


    @classmethod
    def from_yaml_list(cls, yaml_data_list):
        mods = []

        for yaml_data in yaml_data_list:
            mods.append(Module.from_yaml(yaml_data))

        return mods

    def repair_module(self, value_ref):
        keys = value_ref.keys()
        
        if len(keys) == 0:
            return

        for p in self.inputs:
            if hasattr(p, "value") and p.value != None and isinstance(p.value, str) and p.value.startswith("$blueprint."):
                alias_val = value_ref.get(p.value)
                if alias_val != None:
                    p.value = alias_val

        for p in self.outputs:
            if hasattr(p, "value") and p.value != None and isinstance(p.value, str) and p.value.startswith("$blueprint."):
                alias_val = value_ref.get(p.value)
                if alias_val != None:
                    p.value = alias_val
        
        for p in self.settings:
            if hasattr(p, "value") and p.value != None and isinstance(p.value, str) and p.value.startswith("$blueprint."):
                alias_val = value_ref.get(p.value)
                if alias_val != None:
                    p.value = alias_val

        # for p in self.injectors:
        #     if hasattr(p, "value") and p.value != None and isinstance(p.value, str) and p.value.startswith("$blueprint."):
        #         alias_val = value_ref.get(p.value)
        #         if alias_val != None:
        #             p.value = alias_val

    def validate(self) -> List[event.ValidationEvent]:
        mod_validator = module_validator.ModuleModel(self)
        return mod_validator.validate()

    def merge(self, m) -> List[event.ValidationEvent]:
        if self.name != m.name:
            raise ValueError('Module names do not match')
        self.module_type = m.module_type
        self.layer = m.layer
        self.source = m.source
        self.set_inputs(m.inputs)
        self.set_outputs(m.outputs)
        self.set_settings(m.settings)
        self.injectors = m.injectors
        return self.validate()

    def get_acronym(self):
        snips = self.name.split('_')
        if len(snips) <= 1:
            snips = self.name.split('-')
            if len(snips) <= 1:
                snips = self.name.split()
                if len(snips) <= 1:
                    return self.name[:4]

        acy = ''.join([s[0] for s in snips])
        return acy[:4]

    """
    List all linked-data references in the input & setting parameters
    """
    def input_value_refs(self) -> List[str]:
        value_refs = []
        if hasattr(self, "inputs"):
            for p in self.inputs:
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                    value_refs.append(p.value)
        if hasattr(self, "settings"):
            for p in self.settings:
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                    value_refs.append(p.value)
        return value_refs

    """
    List all linked-data references in the output parameters
    """
    def output_value_refs(self) -> List[str]:
        value_refs = []
        if hasattr(self, "outputs"):
            for p in self.outputs:
                if hasattr(p, "value") and isinstance(p.value, str) and (p.value != None and (p.value.startswith("$module.") or p.value.startswith("$blueprint."))):
                    value_refs.append(p.value)
        return value_refs

    """
    Generate the linked-data references for module parameters (inputs, outputs, settings)
    """
    def module_ref(self, key):  # -> (str, event.ValidationEvent):
        (mod_vars, err) = self.input_ref(key)
        if err != None:
            (mod_vars, err) = self.output_ref(key)
            if err != None:
                (mod_vars, err) = self.setting_ref(key)
                if err != None:
                    return (None, event.ValidationEvent(event.BPWarning, 'Module input parameter not found', self))
                else:
                    return mod_vars
            else:
                return mod_vars
        else:
            return mod_vars

    """
    Generate the linked-data references for input parameters
    """
    def input_ref(self, key): # -> (str, event.ValidationEvent):
        if hasattr(self, "inputs"):
            for p in self.inputs:
                if p.name == key:
                    return ("$module." + self.name + ".inputs." + key, None)
        return (None, event.ValidationEvent(event.BPWarning, 'Module input parameter not found', self))

    def input_param(self, key): # -> (param.Input, event.ValidationEvent):
        if hasattr(self, "inputs"):
            for p in self.inputs:
                if p.name == key:
                    return (p, None)
        return (None, event.ValidationEvent(event.BPWarning, 'Module input parameter not found', self))

    def find_input_ref(self, value_ref) -> str: 
        if hasattr(self, "inputs"):
            for p in self.inputs:
                if p.value == value_ref:
                    return p.name
        return None

    def output_ref(self, key): # -> (str, event.ValidationEvent):
        if hasattr(self, "outputs"):
            for p in self.outputs:
                if p.name == key:
                    return ("$module." + self.name + ".outputs." + key, None)
        return (None, event.ValidationEvent(event.BPWarning, 'Module output parameter not found', self))

    def output_param(self, key): # -> (param.Output, event.ValidationEvent):
        if hasattr(self, "outputs"):
            for p in self.outputs:
                if p.name == key:
                    return (p, None)
        return (None, event.ValidationEvent(event.BPWarning, 'Module output parameter not found', self))

    def output_refs(self) -> List[str]: 
        value_refs = []
        if hasattr(self, "outputs"):
            for p in self.outputs:
                value_refs.append("$module." + self.name + ".outputs." + p.name)
        return value_refs

    def find_output_ref(self, value_ref) -> str:
        if hasattr(self, "outputs"):
            for p in self.outputs:
                if p.value == value_ref:
                    return p.name
        return None

    def setting_ref(self, key): # -> (str, event.ValidationEvent):
        if hasattr(self, "settings"):
            for p in self.settings:
                if p.name == key:
                    return ("$module." + self.name + ".settings." + key, None)
        return (None, event.ValidationEvent(event.BPWarning, 'Module settings parameter not found', self))

    def setting_param(self, key): # -> (param.Setting, event.ValidationEvent):
        if hasattr(self, "settings"):
            for p in self.settings:
                if p.name == key:
                    return (p, None)
        return (None, event.ValidationEvent(event.BPWarning, 'Module settings parameter not found', self))

    def find_setting_ref(self, value_ref) -> str:
        if hasattr(self, "settings"):
            for p in self.settings:
                if p.value == value_ref:
                    return p.name
        return None
    
    def list_input_param_names(self) -> List[str]:
        var_names = []
        if self.inputs != None and len(self.inputs) == 0:
            return var_names

        for p in self.inputs:
            var_names.append(p.name)
        
        return var_names

    def list_output_param_names(self) -> List[str]:
        var_names = []
        if self.outputs != None and len(self.outputs) == 0:
            return var_names        

        for p in self.outputs:
            var_names.append(p.name)
        
        return var_names

    def list_setting_param_names(self) -> List[str]:
        var_names = []
        if self.settings != None and len(self.settings) == 0:
            return var_names        

        for p in self.settings:
            var_names.append(p.name)
        
        return var_names

    def set_source(self, source) -> event.ValidationEvent:
        errors = source.validate()
        self.source = source
        return errors

    def set_inputs(self, input_params) -> List[event.ValidationEvent]:
        errors = []
        if(input_params == None):
            self.inputs = []
            return errors
        for param in input_params:
            errors += param.validate()

        # Set the input params, even if there are errors in them
        self.inputs = []
        self.inputs.extend(list(input_params))
        return errors

    def set_outputs(self, output_params) -> List[event.ValidationEvent]:
        errors = []
        if(output_params == None):
            self.outputs = []
            return errors
        for param in output_params:
            errors += param.validate()

        self.outputs = []
        self.outputs.extend(list(output_params))        
        return errors

    def set_settings(self, setting_params) -> List[event.ValidationEvent]:
        errors = []
        if(setting_params == None):
            self.settings = []
            return errors
        for param in setting_params:
            errors += param.validate()

        self.settings = []
        self.settings.extend(list(setting_params))        
        return errors

    def get_input_attr(self, param_name, param_attr):
        for p in self.inputs:
            if p.name == param_name:
                if hasattr(p, param_attr):
                    return getattr(p, param_attr)
                else:
                    return None
        return None

    def set_input_attr(self, param_name, param_attr, param_value) -> List[event.ValidationEvent]:
        errors = []
        param_copy = []
        for p in self.inputs:
            if p.name == param_name:
                setattr(p, param_attr, param_value)
            e = p.validate()
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.inputs = param_copy
        return errors

    def set_input_value(self, param_name, param_value) -> List[event.ValidationEvent]:
        errors = []
        param_copy = []
        for p in self.inputs:
            if p.name == param_name:
                p.value = param_value
            e = p.validate()
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.inputs = param_copy
        return errors

    def update_input(self,
                    input_param: param.Input) -> List[event.ValidationEvent]:
        if self.inputs == None:
            self.inputs = []
        errors = input_param.validate()
        
        # Find and update the input param, even if there are errors in the input_param
        for param in self.inputs:
            if param.name == input_param.name:
                param.type          = input_param.type      if hasattr(input_param, 'type') else None
                param.description   = input_param.description if hasattr(input_param, 'description') else None
                param.value         = input_param.value     if hasattr(input_param, 'value') else None
                param.default       = input_param.default   if hasattr(input_param, 'default') else None
                param.optional      = input_param.optional  if hasattr(input_param, 'optional') else None
                param.comment      = input_param.comment  if hasattr(input_param, 'comment') else None
        
        return errors

    def get_output_attr(self, param_name, param_attr):
        for p in self.outputs:
            if p.name == param_name:
                if hasattr(p, param_attr):
                    return getattr(p, param_attr)
                else:
                    return None
        return None

    def set_output_attr(self, param_name, param_attr, param_value) -> List[event.ValidationEvent]:
        errors = []
        param_copy = []
        for p in self.outputs:
            if p.name == param_name:
                setattr(p, param_attr, param_value)
            e = p.validate()
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.outputs = param_copy
        return errors

    def set_output_value(self, param_name, param_value) -> List[event.ValidationEvent]:
        errors = []
        param_copy = []
        for p in self.outputs:
            if p.name == param_name:
                p.value = param_value
            e = p.validate()
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.outputs = param_copy
        return errors

    def update_output(self,
                    output_param: param.Output) -> List[event.ValidationEvent]:
        if self.outputs == None:
            self.outputs = []
        errors = output_param.validate()
        
        # Find and update the output param, even if there are errors in the output_param
        for param in self.outputs:
            if param.name == output_param.name:
                param.type          = output_param.type     if hasattr(output_param, 'type') else None
                param.description   = output_param.description if hasattr(output_param, 'description') else None
                param.value         = output_param.value    if hasattr(output_param, 'value') else None
                param.comment       = output_param.comment  if hasattr(output_param, 'comment') else None

        return errors

    def get_setting_attr(self, param_name, param_attr):
        for p in self.settings:
            if p.name == param_name:
                if hasattr(p, param_attr):
                    return getattr(p, param_attr)
                else:
                    return None
        return None

    def set_setting_attr(self, param_name, param_attr, param_value) -> List[event.ValidationEvent]:
        errors = []
        param_copy = []
        for p in self.settings:
            if p.name == param_name:
                setattr(p, param_attr, param_value)
            e = p.validate()
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.settings = param_copy
        return errors

    def set_setting_value(self, param_name, param_value) -> List[event.ValidationEvent]:
        errors = []
        param_copy = []
        for p in self.settings:
            if p.name == param_name:
                p.value = param_value
            e = p.validate()
            if len(e) == 0:
                param_copy.append(p)
            errors += e
        self.settings = param_copy
        return errors

    def update_setting(self,
                    setting_param: param.Setting) -> List[event.ValidationEvent]:
        if self.settings == None:
            self.settings = []
        errors = setting_param.validate()
        
        # Find and update the output param, even if there are errors in the output_param
        for param in self.settings:
            if param.name == setting_param.name:
                param.type          = setting_param.type        if hasattr(setting_param, 'type') else None
                param.description   = setting_param.description if hasattr(setting_param, 'description') else None
                param.value         = setting_param.value       if hasattr(setting_param, 'value') else None
                param.default       = setting_param.default     if hasattr(setting_param, 'default') else None
                param.comment       = setting_param.comment     if hasattr(setting_param, 'comment') else None

        return errors

    def add_input(self, input_param) -> event.ValidationEvent:
        if self.inputs == None:
            self.inputs = []
        errors = input_param.validate()

        self.inputs.append(input_param)
        return errors

    def add_inputs(self, input_params) -> List[event.ValidationEvent]:
        if self.inputs == None:
            self.inputs = []
        errors = []
        for param in input_params:
            errors += param.validate()

        self.inputs.extend(list(input_params))        
        return errors

    def add_output(self, output_param) -> event.ValidationEvent:
        if self.outputs == None:
            self.outputs = []
        errors = output_param.validate()

        self.outputs.append(output_param)

        return errors

    def add_outputs(self, output_params) -> List[event.ValidationEvent]:
        errors = []
        if self.outputs == None:
            self.outputs = []
        for param in output_params:
            errors += param.validate()

        self.outputs.extend(list(output_params))

        return errors

    def add_setting(self, setting_param) -> event.ValidationEvent:
        if self.settings == None:
            self.settings = []
        errors = setting_param.validate()

        self.settings.append(setting_param)
        
        return errors

    def add_settings(self, setting_params) -> List[event.ValidationEvent]:
        errors = []
        if self.settings == None:
            self.settings = []
        for param in setting_params:
            errors += param.validate()

        self.settings.extend(list(setting_params))
        return errors

    def delete_output(self, param) -> bool:
        param_copy = []
        found = False
        for p in self.outputs:
            if p.name != param.name:
                param_copy.append(p)
            else:
                found = True
        self.outputs = param_copy
        return found

    def delete_input(self, param) -> bool:
        param_copy = []
        found = False
        for p in self.inputs:
            if p.name != param.name:
                param_copy.append(p)
            else:
                found = True
        self.inputs = param_copy
        return found

    def delete_setting(self, param) -> bool:
        param_copy = []
        found = False
        for p in self.settings:
            if p.name != param.name:
                param_copy.append(p)
            else:
                found = True
        self.settings = param_copy
        return found

#========================================================================
