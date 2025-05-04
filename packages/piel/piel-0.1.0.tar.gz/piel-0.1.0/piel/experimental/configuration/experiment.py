from piel.types.experimental import ExperimentInstance


def generate_experiment_configuration(experiment: ExperimentInstance):
    """
    For a given experiment or physical measurement configuration, we want to generate a given metadata configuration
    describing the measurements that need to be performed and enable us to analyse the data generated from the
    measurement accordingly.

    Ultimately, we want a single file that enables us to encode all the corresponding measurement configuration into
    a single metadata file which streamlines the data acquisition process, especially if it cannot be automated due to
    old equipment.
    """
