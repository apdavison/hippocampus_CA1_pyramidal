"""


"""

from tabulate import tabulate
from datetime import datetime
from hbp_validation_framework import ValidationTestLibrary
from hbp_validation_framework.datastores import CollabDataStore
from hippounit.tests.bpopt import BluePyOpt_MultipleCurrentStepTest

from models import CA1PyramidalNeuron


model_config = {
    "id": "aef2892f-4156-43ad-bdb1-3f5fdaad1240",
    "working_dir": "CA1_pyr_cACpyr_mpg141017_a1-2_idC_20170512161659",
    "template": "CA1_PC_cACnoljp",
    "version": "20170512161659",
    "v_init": -70.0
}
experimental_data = "https://github.com/lbologna/bsp_data_repository/raw/master/optimizations/CA1_pyr_cACpyr_mpg141017_a1-2_idC_20170512161659/CA1_pyr_cACpyr_mpg141017_a1-2_idC_20170512161659.zip"

model = CA1PyramidalNeuron(**model_config)

validation_test = BluePyOpt_MultipleCurrentStepTest(observation=experimental_data,
                                                    plot_figure=True)


#test_library = ValidationTestLibrary(username="adavison")
#validation_test = test_library.get_validation_test("https://validation.brainsimulation.eu/tests/4",
#                                                   plot_figure=True)

score = validation_test.judge(model, deep_error=True)

print(tabulate(score.related_data["score_table"],
               headers=["Feature", "Expt (mean)", "Expt (std)", "Model", "Z"]))
if validation_test.plot_figure:
    print(score.related_data["figures"])
print(score)

# Register the result with the HBP Validation service
# This could be integrated into test.judge() if we extend sciunit appropriately
collab_folder = "{}_{}".format(model.id, datetime.now().strftime("%Y%m%d-%H%M%S"))
collab_storage = CollabDataStore(username="adavison",
                                 collab_id="1771",
                                 base_folder=collab_folder)
test_library.register(score, collab_storage)  # score already linked to test and model (I think)