"""
Script for running vaidation tests of hippocampus CA1 pyramidal neuron models
Works on zip file specified in shell call; user provides file path

Author: Shailesh Appukuttan, CNRS
Date: July 2017

Sequence of steps:
1) Pick the specified ".zip" file
2) Extract this into its individual folders
3) Compile ".mod" files in "mechanisms" sub-directory
4) Check if model is already registered in model catalog; if not then register
5) Collect "model_config" data for model
6) Specify "experimental_data" to be used as reference
7) Create instance of the model and run the test

Usage:
python run_tests_fitted_shellcall.py filename.zip

Files Tested:
CA1_pyr_cACpyr_mpg141017_a1-2_idC_20170512161659.zip
CA1_pyr_cACpyr_mpg141208_B_idA_20170512163148.zip
CA1_int_bAC_060314AM2_20170511120648.zip

Known Issues (to be investigated):
> File: CA1_int_bAC_011017HP2_20170510120000.zip
Error: NEURON: eof call nested too deeply, increase with -NFRAME framesize option
"""

import argparse
from os.path import basename
from zipfile import ZipFile
import os
import ast
from tabulate import tabulate
from datetime import datetime
from models import CA1PyramidalNeuron
from hippounit.tests.bpopt import BluePyOpt_MultipleCurrentStepTest
from hbp_validation_framework import ModelRepository
from hbp_validation_framework.datastores import CollabDataStore
from hbp_validation_framework import ValidationTestLibrary

hbp_username = "shailesh"
# where to extract zip files locally; also used for storing output files
base_output_dir = "./model_files/"

#===============================================================================
"""
1) Pick the specified ".zip" file
"""
parser = argparse.ArgumentParser()
parser.add_argument("path", help="path of zip file with extension")
config = parser.parse_args()

zip_file = config.path
zip_name = basename(zip_file)[:-4]

#===============================================================================
"""
2) Extract this into its individual folders
"""
zip_ref = ZipFile(zip_file, 'r')
zip_ref.extractall(base_output_dir)
zip_ref.close()

#===============================================================================
"""
3) Compile ".mod" files in "mechanisms" sub-directory
"""
shell_cmd =  "(cd " + base_output_dir + zip_name + "/mechanisms && nrnivmodl)"
os.system(shell_cmd)

#===============================================================================
"""
4) Check if model is already registered in model catalog; if not then register
Note: Model name is considered as the zip name till the last underscore
"""
model_library = ModelRepository(hbp_username)
model_catalog = model_library.list_models()

model_exists = False
zip_model_name = zip_name.rsplit('_', 1)[0]
for model in model_catalog:
   if zip_model_name == model["name"]:
      print zip_model_name + " : Model already registered in Model Catalog."
      model_exists = True
      break
if model_exists == False:
   print zip_model_name + " : Registering Model in Model Catalog."
   model_library.register(name=zip_model_name, description="Fill Later",
                          species="rat", brain_region="hippocampus CA1",
                          cell_type="pyramidal",
                          author="Rosanna Migliore, CNR <rosanna.migliore@cnr.it>",
                          source="	https://github.com/lbologna/bsp_data_repository")

#===============================================================================
"""
5) Collect "model_config" data for model
(Could be combined with above step; need a method to obtain "model_uri" for
newly added models, i.e. where model_exists==False)
"""
model_config = {}

zip_model_name = zip_name.rsplit('_', 1)[0]
for model in model_catalog:
   if zip_model_name == model["name"]:
      with open(base_output_dir+zip_name+"/config/morph.json", 'r') as f_morph, open(base_output_dir+zip_name+"/config/parameters.json", 'r') as f_param:
         model_template = ast.literal_eval(f_morph.read()).keys()[0]
         model_dict_temp = {
                              "id": model["resource_uri"].rsplit('/',1)[1],
                              "working_dir": base_output_dir+zip_name,
                              "template": model_template,
                              "version": zip_name.rsplit('_', 1)[1],
                              "v_init": -70.0
                           }
         model_globals = ast.literal_eval(f_param.read())[model_template]["fixed"]["global"]
         for key, val in model_globals:
            model_dict_temp[key] = val
         model_config = (model_dict_temp)
      break

#===============================================================================
"""
6) Specify "experimental_data" to be used as reference
"""
base_path = "https://github.com/lbologna/bsp_data_repository/raw/master/optimizations/"
expt_path = zip_name+"/"+zip_name+".zip"
experimental_data = base_path+expt_path

#===============================================================================
"""
7) Create instance of the model and run the test
"""
model = CA1PyramidalNeuron(**model_config)
validation_test = BluePyOpt_MultipleCurrentStepTest(observation=experimental_data,
                                                    plot_figure=True)

validation_test.id = "/tests/4?version=5"
score = validation_test.judge(model, deep_error=True)
print(tabulate(score.related_data["score_table"],
               headers=["Feature", "Expt (mean)", "Expt (std)", "Model", "Z"]))

if "figures" in score.related_data:
    print(score.related_data["figures"])
print(score)

# Register the result with the HBP Validation service
# This could be integrated into test.judge() if we extend sciunit appropriately
collab_folder = "{}_{}".format(model.id, datetime.now().strftime("%Y%m%d-%H%M%S"))
collab_storage = CollabDataStore(collab_id="1771",
                                 base_folder=collab_folder)
test_library = ValidationTestLibrary(username=hbp_username)
test_library.register(score, project="1771", data_store=collab_storage)  # score already linked to test and model (I think)

#===============================================================================
