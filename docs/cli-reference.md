## CLI Illustrations

Sample CLIs commands that you can use to try to learn about the toolset.

### Blueprint validate tool
   * `blueprint validate -b ./examples/validate/data/detection-rule.yaml`
   * `blueprint validate -b detection-rule.yaml -s ./examples/validate/data`
   * `blueprint validate -b detection-rule.yaml -s ./examples/validate/data -j` in the `json` output format.
  
    Note: The `detection-rule.yaml` is a sample blueprint configuration file. Refer to other examples in the same folder.

---
### Blueprint merge tool
   * `blueprint merge -m ./examples/merge/data-1/manifest.yaml -o ./merged-bp.yaml`
     * generates the merged blueprint file in `./merged-bp.yaml`
   * `blueprint merge -m manifest.yaml -s ./examples/merge/data-1 -o ./merged-bp.yaml`
   * `blueprint merge -m manifest.yaml -s ./examples/merge/data-1 -o ./merged-bp.yaml -j` 
    
    Note: The `manifest.yaml` file is a sample blueprint manifest file that combines multiple code snippets in the same folder.

---
### Blueprint sync tool
   * `blueprint sync -b ./examples/sync/data/bplite.yaml -w ./temp -o ./synced-bp.yaml` 
     * pre-req: install terraform-config-inspect, and setup the environment $TERRAFORM_CONFIG_INSPECT_PATH
     * uses `./temp` folder to download & process intermediate files; 
     * generates the output blueprint file in `./synced-bp.yaml`
   * `blueprint sync -b bplite-1.yaml -s ./examples/sync/data -w ./temp -o ./synced-bp.yaml` 

---
### Blueprint run tool
  * `blueprint run -c apply -d -b ./examples/run/data/sample1.yaml -i ./examples/run/data/input_data1.yaml -w ./temp`
    * pre-req: install terraform-config-inspect, and setup the environment $TERRAFORM_CONFIG_INSPECT_PATH.
    * pre-req: install Terraform CLI.
    * uses `./examples/run/data/sample1.yaml` as the blueprint configuration file.
    * uses `./examples/run/data/input_data1.yaml` as the input data file for the blueprint configuration.
    * `-d` will trigger a dry-run for the `blueprint apply` command.
    * uses `./temp` as the working directory to generate the temporary terraform files (due to a dry-run) and run the Terraform Apply command.
  * `blueprint run -c apply -b ./examples/run/data/sample1.yaml -i ./examples/run/data/input_data1.yaml -w ./temp`
    * pre-req: install terraform-config-inspect, and setup the environment $TERRAFORM_CONFIG_INSPECT_PATH.
    * pre-req: install Terraform CLI.
    * uses `./examples/run/data/sample1.yaml` as the blueprint configuration file.
    * uses `./examples/run/data/input_data1.yaml` as the input data file for the blueprint configuration.
    * uses `./temp` as the working directory to download and run the Terraform Apply commands.

---
### Blueprint draw tool
    * `blueprint draw -b ./examples/draw/data/sample1.yaml -t viz -w ./temp`
      * Generate a `out_blueprint.png file` (default name) by using the `./examples/draw/data/sample1.yaml` as the input blueprint configuration file.
      * The output format is a GraphViz format.
    * `blueprint draw -b ./examples/draw/data/sample1.yaml -t ic -w ./temp`
      * The output format is an Integrated Circuit format.
  
