## 1. How to validate the `blueprint configuration file` ?

You can use the following command-line to validate the `blueprint configuration file`.

> blueprint validate [-h] -b BP_FILE [-w WORKING_DIR]

It performs two levels of validation
1. YAML Schema validation - to verify whether your blueprint _yaml_ file, is compliant to the prescribed schema.
2. Advanced semantic validation - to verify whether the input and output variable definitions are used correctly, and linked properly.

The result of validation can be obtained in _tabular_ or _json_ format.

---
### List of advanced validation

| Sl | Validation message | Description and remmediation |
|----|--------------------|----------------------------|
| 1 | Unused input parameters declared in the blueprint | Blueprint input variable from the `inputs` section is not being used by any module.  </br>Review the linked-data references for example, `$blueprint.inputs.vpc_zone` in all the modules, to ensure that it is being named & used correctly. | 
| 2 | Undeclared blueprint parameters used by modules | A module is referring to an input variable that has not been declared in the `inputs` section of the blueprint. </br>Review the linked-data reference in the specified module for example, `$blueprint.inputs.vpc_zone` for any spelling mistakes or capitalization. |
| 3 | Undeclared output parameters used by modules | A module is referring to an output variable that has not been declared in the `outputs` section of another module. </br>Review the linked-data reference in the specified module for example, `$modules.mod_name.outputs.vpc_zone` for any spelling mistakes or capitalization. |
| 4 | Unused output parameters declared in the modules | A module has declared an output variable, that is not be used or referred by other modules, or the outputs of the blueprint. </br>Review the linked-data references for example, `$modules.mod_name.outputs.vpc_zone` in all the modules and the blueprint outputs to ensure that it is named and used correctly. |
| 5 | Blueprint output parameters is left hanging | The output variable that is declared in the `outputs` section of the blueprint do not have a valid linked-data reference, to the outputs produced by a module in the blueprint. </br>Ensure that all the blueprint outputs have cross-references or links to the correct module output variable.|
| 6 | Found circular dependencies between modules | The links between the input and output variables in all the modules has resulted in a circular dependency. For example, module 1 to module 2, module 2 to module 3, module 3 to module 1.  </br>Review all the links between the input and output variables, to ensure that there is no circular dependencies between the modules. |
| 7 | Error in the input parameters for the modules | The input variable of a module, does not have any input values or linked-data specified. </br>Review the module input variable definition, and ensure that there value or default attribute is not blank. |
| 8 | Duplicate parameter names in the module | The module has duplicate variable name. |
| 9 | Self referential values in the module | The output variable of the module is linked to the input variable of the same module. Or the input variable of the module is linked to the output variable of the same module. </br>Review the linked-data specification of the input and output variables in the module, and ensure that variables refers to the correct modules. |
| 10 | Type mismatch for boolean parameter | The values assigned to the input, output, or settings variable does not match the boolean type, specified for that variable. |
| 11 | Input parameter is not initialized with any value | The `input` variable is not initialized with any value or the linked-data reference.|
| 12 | Setting parameter is not initialized with any value | The `setting` variable is not initialized with any value or the linked-data reference.|
{: caption="List of advanced validation" caption-side="bottom"}

---

### Programmatic blueprint validation

In addition you can progamatically validate your `blueprint configuration file` by using the following Python modules.
* blueprint.validate.schema_validator.SchemaValidator
* blueprint.validate.blueprint_validator.BlueprintModel

As illustrated in the following code snippet:

```python
    input_file = 'blueprint.yaml' 

    # Perform Blueprint schema validation               #
    ##=================================================##
    bsv = schema_validator.SchemaValidator(input_file)
    (msg, err) = bsv.validate()
    if err != None:
        eprint(err)
    
    # Load Blueprint yaml file, for advanced validation #
    ##=================================================##
    bp = bfile.FileHelper.load_blueprint(input_file)
    if bp == None:
        eprint("Error in loading the blueprint file")

    # Perform advanced semantic validation of Blueprint #
    ##=================================================##
    bpv = blueprint_validator.BlueprintModel(bp)
    err = bpv.validate()
    if err != None:
        eprint(event.format_events(err, event.Format.Table))

```

---
### Next steps

After validating your blueprint configuration or static analysis, you can perform the following operations.
* [Visualize the blueprint configuration](./07-visualize.md) to visually inspect the connections between the blueprint and modules, and between the modules and modules.
* [Dry-run the blueprint configuration](./06-run.md) to verify a mock data-flow for dynamic analysis
* (Optionally) [Run the blueprint configuration](./06-run.md) locally by using the local copy of the Terraform CLI.
  > Warning Note: This step will incur cost of provisioning the Cloud resource)
* (Optionally) Onboard the blueprint configuration to the IBM Cloud Schematics, to [run the blueprint](https://cloud.ibm.com/docs/schematics?topic=schematics-create-blueprint-config&interface=ui) remotely.

---
