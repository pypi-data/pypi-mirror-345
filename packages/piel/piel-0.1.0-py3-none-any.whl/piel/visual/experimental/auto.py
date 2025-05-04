from piel.types import PathTypes
from piel.types.experimental import (
    MeasurementDataTypes,
    MeasurementDataCollectionTypes,
    ExperimentData,
)
from .map import (
    measurement_data_collection_to_plot_map,
    measurement_data_to_plot_map,
    measurement_data_collection_to_plot_suffix_map,
)
from piel.experimental.analysis.operating_point import (
    create_experiment_data_collection_from_unique_parameters,
)
from piel.file_system import return_path


def auto_plot_from_measurement_data(
    measurement_data: MeasurementDataTypes,
    **kwargs,
) -> list[tuple, PathTypes]:
    """
    This function will automatically plot the data from the `MeasurementData` object provided.
    If there are more than one set of relevant plots for a given `MeasurementData`,
    it will generate a list of figures accordingly.
    """
    plots = []
    plot_methods = measurement_data_to_plot_map[measurement_data.type]
    for plot_method_i in plot_methods:
        plot_i = plot_method_i(measurement_data, **kwargs)
        plots.append(plot_i)

    return plots


def auto_plot_from_measurement_data_collection(
    measurement_data_collection: MeasurementDataCollectionTypes,
    plot_output_directory: PathTypes = None,
    extra_plot_output_directories: list[PathTypes] = None,
    measurement_data_collection_to_plot_map: dict = measurement_data_collection_to_plot_map,
    measurement_data_collection_to_plot_prefix_map: dict = measurement_data_collection_to_plot_suffix_map,
    **kwargs,
) -> tuple[list[tuple], list[PathTypes]]:
    """
    This function will automatically plot the data from the `MeasurementDataCollection` provided.
    If there are more than one set of relevant plots for a given `MeasurementData`,
    it will generate a list of figures accordingly.
    """
    plots = []
    plot_path_list = []
    extra_plot_file_paths = []
    plot_output_directory = return_path(plot_output_directory)

    # This creates the mapping between measureemnt collection and the corresponding plots
    plot_methods = measurement_data_collection_to_plot_map[
        measurement_data_collection.type
    ]

    plot_prefix = measurement_data_collection_to_plot_prefix_map[
        measurement_data_collection.type
    ]

    i = 0
    # We iterate through the corresponding plotting methods and generate the plots, and save them to the parent directory.
    for plot_method_i in plot_methods:
        file_name = f"{plot_prefix[i]}_{measurement_data_collection.name}"
        plot_file_i = plot_output_directory / f"{file_name}.png"

        if extra_plot_output_directories is not None:
            extra_plot_file_paths = []
            for extra_plot_output_directory_i in extra_plot_output_directories:
                extra_plot_output_directory_i = return_path(
                    extra_plot_output_directory_i
                )
                extra_plot_file_i = extra_plot_output_directory_i / f"{file_name}.png"
                extra_plot_file_paths.append(extra_plot_file_i)

        plot_i = plot_method_i(
            measurement_data_collection,
            path=plot_file_i,
            paths=extra_plot_file_paths,
            **kwargs,
        )
        plots.append(plot_i)
        plot_path_list.append(plot_file_i)
        i += 1

    return plots, plot_path_list


def auto_plot_from_experiment_data(
    experiment_data: ExperimentData,
    plot_output_directory: PathTypes = None,
    parametric: bool = False,
    **kwargs,
) -> tuple[list[tuple], list[PathTypes]]:
    """
    This function will automatically plot the data from the `ExperimentData` object provided.
    """
    plots = []
    plot_path_list = []
    if parametric:
        # Here we fill first extract all the corresponding parametric `ExperimentData`
        experiment_data_collection = (
            create_experiment_data_collection_from_unique_parameters(
                experiment_data=experiment_data
            )
        )

        for experiment_data_i in experiment_data_collection.collection:
            print(experiment_data_i.name)
            print(experiment_data_i.experiment.parameters)

            # Default just plots a single set of parametric plots.
            plots_i, plot_path_list_i = auto_plot_from_measurement_data_collection(
                measurement_data_collection=experiment_data_i.data,
                plot_output_directory=plot_output_directory,
                parameters_list=experiment_data_i.experiment.parameters_list,
                **kwargs,
            )
            plots += plots_i
            plot_path_list += plot_path_list_i

    else:
        # Default just plots a single set of parametric plots.
        plots_i, plot_path_list_i = auto_plot_from_measurement_data_collection(
            measurement_data_collection=experiment_data.data,
            plot_output_directory=plot_output_directory,
            parameters_list=experiment_data.experiment.parameters_list,
            **kwargs,
        )
        plots += plots_i
        plot_path_list += plot_path_list_i

    return plots, plot_path_list
