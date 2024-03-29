
## 6. How to codify a `blueprint configuration file` in Python?

Manually developing a blueprint configuration file in `yaml` format by using an IDE or text editor is error prone. You must go through several cycles of trial and error.

What-if, you have the ability to codify your blueprint automation by using Python, validate, and run the automation.

### 6.1 Programming your cloud (green-field)

Start afresh to program your Cloud automation, by using the Blueprint Python library

#### Blueprint Python library usage

  Use the `blueprint Python library` to assemble the blueprint configuration file by using Python.

  The library includes the following schema elements that can be used to define your blueprint manifest
  * schema.blueprint.Blueprint
  * schema.module.Module
  * schema.source.TemplateSource
  * schema.source.GitSource
  * schema.source.CatalogSource
  * schema.param.Input
  * schema.param.Output
  * schema.param.Setting

Initialize your blueprint

```python
    bp = blueprint.Blueprint(
        name        = "Blueprint Basic Example",
        description = "Simple blueprint to demonstrate module linking",
    )
```

Add input, output, and settings parameter to the blueprint.

```python
    bp_storage_name = param.Input(name = "bp_storage_name")
    bp_storage_plan = param.Input(name = "bp_storage_plan")
    bp_storage_id   = param.Output(name = "bp_storage_id")
    bp_tf_settings  = param.Setting(name = "TF_VERSION", value = "1.0")
    err = []
    err += bp.set_inputs([
            bp_storage_name,
            bp_storage_plan,
        ])

    err += bp.set_outputs([
            bp_storage_id
        ])

    err += bp.set_settings([
            bp_tf_settings
        ])
```

You can use the `err` to accumulate the `ValidationEvent` while creating the blueprint configuration.

Create a module for the blueprint

```python
    cos_mod = module.Module(
        name        = "basic-cos-storage", 
        type        = module.TerraformType
    )
```

Add source, input, output, and settings parameter to the module.

```python
    cos_instance_name      = param.Input(name = "cos_instance_name")
    cos_storage_plan       = param.Input(name = "cos_storage_plan")
    cos_single_site_loc    = param.Input(name = "cos_single_site_loc", value = "ams03")
    cos_resource_group_id  = param.Input(name = "resource_group_id")
    cos_id                 = param.Output(name = "cos_id")
    cos_crn                = param.Output(name = "cos_crn")

    storage_mod_source = source.TemplateSource(
                    type = "github", 
                    git = source.GitSource(
                        repo_url = "https://github.com/Cloud-Schematics/blueprint-example-modules/tree/main/IBM-Storage",
                        branch = "main"
                    )
                )
    err = []
    err += cos_mod.set_source(storage_mod_source)
    err += cos_mod.set_inputs([
                    cos_instance_name, 
                    cos_storage_plan, 
                    cos_single_site_loc, 
                    cos_resource_group_id, 
                ])
    err += cos_mod.set_outputs([
                    cos_id,
                    cos_crn
                ])
```

Add module to the blueprint.

```python
    bp.add_module(cos_mod)
```

Use a bus to connect blueprint to module, or module to a module.

```python
    bp_bus = bus.WireBus(bp, cos_mod)
    mod_bus = bus.WireBus(rg_mod, cos_mod)
```

Add wires to the bus to connect the input and output variables.

```python
    err += bp_bus.add_wire('bp_storage_name', 'cos_instance_name')
    err += mod_bus.add_wire('resource_group_id', 'resource_group_id')
```

Emit the `blueprint configuration file`, as an `yaml` file.

```python
    (bpyaml, errors) = bp.to_yaml_str()
    if len(errors) != 0:
        eprint(event.format_events(err, event.Format.Table)) # or event.Format.Json
    else:
        print(bpyaml)
```

Emit a `sample input file`, for the blueprint configuration, as an `yaml` file.

```python
    sample_inputs = bp.generate_input_file()
    print(sample_inputs)

```

### 6.2 Extending your cloud automation

When you already have a blueprint configuration file, and want to extend it programmatically with more modules, modify the input and output wiring, and so on.

The first step is to import your blueprint configuration file.

```python

    filename = 'existing_blueprint.yaml'

    print("Loading blueprint file " + filename + " ...")
    with open(filename) as f:
        yaml_str = f.read()
        bp = blueprint.Blueprint.from_yaml_str(yaml_str)

```

Further, you can validate the blueprint configuration, for any known errors.

```python
    err = bp.validate()
    
    if len(err) != 0:
        print("Found validation errors !\n")
        eprint(event.format_events(err, event.Format.Table)) # or event.Format.Json
```

Now you have the Python blueprint object that can add following modules to extend.
* add new module.Module (modify existing module)
* add new circuit.WireBus (add or modify Wires in the WireBus)

### 6.3 Run your cloud automation

After you have a validated a blueprint object in memory, you can do the following:
* dry-run the blueprint 
* run the blueprint

Following are the prerequisite to run the blueprint in your local machine.
* [Terraform CLI (version 1.0 or higher)](https://cloud.ibm.com/docs/ibm-cloud-provider-for-terraform?topic=ibm-cloud-provider-for-terraform-setup_cli)
* Setup the environment variables with your API Keys (as needed by the respective Terraform providers)

The first step is to setup a `BlueprintRunner`:

```python
   br = bprunner.BlueprintRunner(blueprint_file = blueprint_file, 
                                 input_data_file = input_data_file, 
                                 dry_run = True,
                                 working_dir = working_dir)

```

The `BlueprintRunner` uses the `working_dir` to create multiple folders (one each for the modules in the blueprint configuration file). Further, it downloads the Terraform modules from the source (Git repositories), and prepares itself to run the Terraform command.

When you choose to `dry_run` the blueprint module, the Terraform modules are not downloaded from the Git repositories, instead - the input or output configurations in the blueprint is used to automatically generate a set of Terraform module (with the `vars.tf` and `output.tf` along with a dummy null_resource), and are placed in the `working_dir`\folders. You can customize the values in the input and output variables to simulate data-flows between the modules in the blueprint configuration. It can be used for dynamic analysis of the blueprint configuration.

You can use the following Python code to perform `blueprint init`, `blueprint plan`, `blueprint apply`, and `blueprint destroy`.

When you run these commands, the in-built orchestrator switches to the respective modules-specific folders, and run the corresponding Terraform CLI command. The outputs that are produced by the Terraform Apply commands are chained (or fed as input) to the down-stream Terraform module by the orchestrator.

Blueprint init
```python
    err = br.init_modules()
    print("Init errors \n" + event.format_events(err, event.Format.Table))
```

Blueprint plan
```python
    err = br.plan_modules()
    print("Plan errors \n" + event.format_events(err, event.Format.Table))
```

Blueprint apply
```python
    err = br.apply_modules()
    print("Apply errors \n" + event.format_events(err, event.Format.Table))
```

Blueprint destroy
```python
    err = br.destroy_modules()
    print("Destroy errors \n" + event.format_events(err, event.Format.Table))
```

### 6.3 Visualize your cloud automation

Before running your blueprint configuration, you need to visualize the dependencies between the blueprint and modules, and the dependencies between the modules in the blueprint. You can generate two types of network diagrams and save them to a file in `png`, or `jpg` format.

Draw a graphviz network diagram

```python
   br = bpdraw.BlueprintDraw(blueprint_file = blueprint_file)
   br.prepare()
   br.draw()
```

Draw a schemdraw circuit diagram

```python
   br = board.BlueprintBoard(blueprint_file = blueprint_file)
   br.prepare(width=20, height=15)
   br.draw(shape='a', bend='z')
```

---
