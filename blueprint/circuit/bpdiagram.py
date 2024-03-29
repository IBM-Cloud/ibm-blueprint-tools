from diagrams import Diagram, Node, Cluster, Edge

import html
import textwrap
from typing import List, Union
import diagrams

def _format_text(text):
    """
    Formats the node description
    """
    wrapper = textwrap.TextWrapper(width=40, max_lines=3)
    lines = [html.escape(line) for line in wrapper.wrap(text)]
    lines += [""] * (3 - len(lines))  # fill up with empty lines so it is always three
    return "<br/>".join(lines)

#=======================================================================================#

class BlueprintPane(Cluster):

    def __init__(
                self,
                name: str = "cluster",
                description: str = "",
                inputs: List[str] = [], 
                outputs: List[str] = [],
                settings: List[str] = [],
                **kwargs
            ):
        """
        BlueprintPane represents a Blueprint cluster context.

        :param name: Blueprint name.
        :param description: Blueprint description 
        :param inputs: List of input parameter names for the Blueprint
        :param outputs: List of output parameter names for the Blueprint
        :param settings: List of env setting parameter names for the Blueprint
        """

        graph_attr = {
                    "label": html.escape(name),
                    "bgcolor": "white",
                    "margin": "16",
                    "style": "dashed",
                    "direction": "LR"
                }
        super().__init__(label = name, direction = "LR", graph_attr = graph_attr, **kwargs)
        diagrams.setcluster(self)
        self.in_bp_node = ModulePane('in:'+name, description,
                inputs, [], settings, 
                type = "Blueprint")

        self.out_bp_node = ModulePane('out:'+name, description,
                [], outputs, [], 
                type = "Blueprint")

    def _format_blueprint_label(self, name, description, inputs, outputs, settings):
        """
        Create a graphviz label string for BlueprintPane - name, inputs, outputs, settings;
        """
        title = f'<font point-size="14"><b>{html.escape(name)}</b></font><br/>'
        subtitle = f'<font point-size="12">-------------------------------<br/></font>'
        subtitle += f'<font point-size="9">[{_format_text(description)}]<br/></font>' if description else ""
        text = f'<font point-size="12">-------------------------------<br/></font>' if description else ""
        if inputs != None:
            for i in inputs:
                text += f'<font point-size="12">input: {_format_text(i)}</font>' if i else ""
        if outputs != None:
            for o in outputs:
                text += f'<font point-size="12">output: {_format_text(o)}</font>' if o else ""
        if settings != None:
            for s in settings:
                text += f'<font point-size="12">setting: {_format_text(s)}</font>' if s else ""

        return f"<{title}{subtitle}{text}>"

#=======================================================================================#

class ModulePane(Node):
    def __init__(
                self, 
                name: str, 
                description: str = "",
                inputs: List[str] = [], 
                outputs: List[str] = [],
                settings: List[str] = [], 
                type: str = "Module",
                **kwargs
            ):
        """
        ModulePane represents a module component in a blueprint

        :param name: Name of the module.
        :param inputs: List of input parameter names 
        :param outputs: List of output parameter names 
        :param settings: List of environment parameter names 
        """
        self.name = name

        line_count = len(inputs) + len(outputs) + len(settings)
        height = 0.5 * (line_count+1)
        key = f"{type}"
        node_attributes = {
            "label": self._format_module_label(name, key, description, inputs, outputs, settings),
            "labelloc": "u",
            "shape": "rect",
            "width": "2.6",
            "height": str(height),
            "fixedsize": "false",
            "style": "filled",
            "fillcolor": self._module_color(type),
            "fontcolor": "white",
        }
        
        super().__init__(**node_attributes, **kwargs)
    
    def _module_color(self, type):
        if type.lower() == "module":
            return "gold4"
        elif type.lower() == "blueprint":
            return "dodgerblue3"
        else:
            return "gray30"

    def _format_module_label(self, name, key, description, inputs, outputs, settings):
        """
        Create a graphviz label string for ModulePane - name, inputs, outputs, settings;
        """
        title = f'<font point-size="14"><b>{html.escape(name)}</b></font><br/>'
        subtitle = f'<font point-size="9">[{html.escape(key)}]<br/></font>' if key else ""
        subtitle += f'<font point-size="12">-------------------------------<br/></font>'
        subtitle += f'<font point-size="9">[{_format_text(description)}]<br/></font>' if description else ""
        text = f'<font point-size="12">-------------------------------<br/></font>' if description else ""
        if inputs != None:
            for i in inputs:
                text += f'<font point-size="12">input: {_format_text(i)}</font>' if i else ""
        if outputs != None:
            for o in outputs:
                text += f'<font point-size="12">output: {_format_text(o)}</font>' if o else ""
        if settings != None:
            for s in settings:
                text += f'<font point-size="12">setting: {_format_text(s)}</font>' if s else ""

        return f"<{title}{subtitle}{text}>"

    def __str__(self) -> str:
        return str(self.name)

    # def __rshift__(self, other: Union["ModulePane", List["ModulePane"], "Relation"]):
    #     """Implements Self >> ModulePane, Self >> [ModulePanes] and Self Relation."""
    #     if isinstance(other, list):
    #         print("N1:" + str(other))
    #     elif isinstance(other, ModulePane):
    #         print("N2:" + str(other))
    #     else:
    #         print("N3:" + str(other))

    #     super().__rshift__(other)

    # def __lshift__(self, other: Union["ModulePane", List["ModulePane"], "Relation"]):
    #     super().__lshift__(other)

    # def __rrshift__(self, other: Union[List["ModulePane"], List["Relation"]]):
    #     """Called for [ModulePanes] and [Relations] >> Self because list don't have __rshift__ operators."""
    #     print("N4: " + str(other))
    #     if other != None:
    #         super().__rrshift__(other)

    # def __rlshift__(self, other: Union[List["ModulePane"], List["Relation"]]):
    #     """Called for [ModulePanes] << Self because list of ModulePanes don't have __lshift__ operators."""
    #     print("N5: " + str(other))
    #     if other != None:
    #         super().__rlshift__(other)

#=======================================================================================#
class Relation(Edge):

    def __init__(
                self,
                from_param: str = None, 
                to_param: str = None,
                edge_attributes = {"style": "dashed", "color": "gray60"},
                **kwargs
            ):
        """
        Relation connects the output of one module to inputs of another module.

        :param from_param: From module output parameter name
        :param to_param: To module input parameter name
        :param edge_attributes: Drawing attributes for the edge
        """
        self.name = f'{from_param} >> {to_param}'
        if from_param and to_param:
            label = from_param + '-->>--' + to_param
            edge_attributes.update({"label": self._format_wire_label(label)})
        
        super().__init__(**edge_attributes, **kwargs)

    def _format_wire_label(self, description):
        """
        Create a graphviz label string for a Relation that connects two modules
        """
        wrapper = textwrap.TextWrapper(width=24, max_lines=3)
        lines = [html.escape(line) for line in wrapper.wrap(description)]
        text = "<br/>".join(lines)
        return f'<<font point-size="12">{text}</font>>'

    def __str__(self) -> str:
        return str(self.name)

    # def __rshift__(self, other: Union["ModulePane", "Relation", List["ModulePane"]]):
    #     """Implements Self >> ModulePane or Relation and Self >> [ModulePanes]."""
    #     if isinstance(other, list):
    #         print("E1:" + str(other))
    #     elif isinstance(other, ModulePane):
    #         print("E2:" + str(other))
    #     else:
    #         print("E3:" + str(other))

    #     super().__rshift__(other)

    # def __lshift__(self, other: Union["ModulePane", "Relation", List["ModulePane"]]):
    #     """Implements Self << ModulePane or Relation and Self << [ModulePanes]."""
    #     super().__lshift__(other)

    # def __rrshift__(self, other: Union[List["ModulePane"], List["Relation"]]) -> List["Relation"]:
    #     """Called for [ModulePanes] or [Relations] >> Self because list of Relations don't have __rshift__ operators."""
    #     print("E4: " + str(other))
    #     if other != None:
    #         super().__rrshift__(other)

    # def __rlshift__(self, other: Union[List["ModulePane"], List["Relation"]]) -> List["Relation"]:
    #     """Called for [ModulePanes] or [Relations] << Self because list of Relations don't have __lshift__ operators."""
    #     print("E5: " + str(other))
    #     if other != None:
    #         super().__rlshift__(other)

#=======================================================================================#