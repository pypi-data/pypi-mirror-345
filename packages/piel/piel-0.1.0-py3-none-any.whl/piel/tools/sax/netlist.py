"""
This module aims to extend sax from standard netlist operations to include more complex operations that enable connectivity.
"""

from typing import Optional
from ...models.frequency import get_default_models


def address_value_dictionary_to_function_parameter_dictionary(
    address_value_dictionary: dict,
    parameter_key: str,
):
    """
    Converts a dictionary of address-value pairs to a dictionary of function parameters.

    Args:
        address_value_dictionary (dict): Dictionary where the key is a tuple of (component, instance, parameter) and the value is the parameter's value.
        parameter_key (str): The key under which the parameter value will be stored in the output dictionary.

    Returns:
        dict: A nested dictionary where each instance has a dictionary of parameters with their corresponding values.

    Example:
        Input:
            {('component_lattice_gener_fb8c4da8', 'mzi_1', 'sxt'): 0,
             ('component_lattice_gener_fb8c4da8', 'mzi_5', 'sxt'): 0}

        Output:
            {'mzi_1': {'sxt': {parameter_key: 0}},
             'mzi_5': {'sxt': {parameter_key: 0}}}

    This function processes a dictionary of component addresses and parameter values, converting it into a nested dictionary format that is suitable for use as function parameters.
    """
    result = {}
    for (_, instance, param), value in address_value_dictionary.items():
        if instance not in result:
            result[instance] = {}
        result[instance][param] = {parameter_key: value}
    return result


def compose_recursive_instance_location(
    recursive_netlist: dict,
    top_level_instance_name: str,
    required_models: list,
    target_component_prefix: str,
    models: dict,
):
    """
    This function returns the recursive location of any matching ``target_component_prefix`` instances within the
    ``recursive_netlist``. A function that returns the mapping of the ``matched_component`` in the corresponding
    netlist at any particular level of recursion. This function iterates over a particular level of recursion of a
    netlist. It returns a list of the missing required components, and updates a dictionary of measurement that contains a
    particular matching component. It returns the corresponding list of instances of a particular component at that
    level of recursion, so that it can be appended upon in order to construct the location of the corresponding
    matching elements.

       If ``required_models`` is an empty list, it means no recursion is required and the function is complete. If a
       ``required_model_i`` in ``required_models`` matches ``target_component_prefix``, then no more recursion is
       required down the component function.

       The ``recursive_netlist`` should contain all the missing composed measurement that are not provided in the main
       measurement dictionary. If not, then we need to require the user to input the missing model that cannot be
       extracted from the composed netlist. We know when a model is composed, and when it is already provided at
       every level of recursion based on the ``measurement`` dictionary that gets updated at each level of recursion with
       the corresponding measurement of that level, and the ``required_models`` down itself.

       However, a main question appears on how to do the recursion. There needs to be a flag that determines that the
       recursion is complete. However, this is only valid for every particular component in the ``required_models``
       list. Every component might have missing component. This means that this recursion begins component by
       component, updating the ``required_models`` list until all of them have been composed from the recursion or it
       is determined that is it missing fully.

       It would be ideal to access the particular component that needs to be implemented.

       Returns a tuple of ``model_composition_mapping, instance_composition_mapping, target_component_mapping`` in the form of

           ({'mzi_214beef3': ['straight_heater_metal_s_ad3c1693']},
            {'mzi_214beef3': ['mzi_1', 'mzi_5'],
             'mzi_d46c281f': ['mzi_2', 'mzi_3', 'mzi_4']})

       Args:
        recursive_netlist (dict): The hierarchical netlist dictionary.
        top_level_instance_name (str): The name of the top-level instance to start the search from.
        required_models (list): A list of measurement that need to be included in the recursion.
        target_component_prefix (str): The prefix of the component instances to locate.
        models (dict): A dictionary of measurement provided to aid in the recursion.

        Returns:
            tuple: A tuple containing:
                - model_composition_mapping (dict): A mapping of required measurement to their composed measurement.
                - instance_composition_mapping (dict): A mapping of required measurement to their corresponding instances.
                - target_component_mapping (dict): A mapping of target components to their parent components.

    """
    import sax

    model_composition_mapping = dict()
    instance_composition_mapping = dict()
    target_component_mapping = dict()
    i = 0

    while len(required_models) != 0:
        # if len(required_models) == 0:
        #     pass
        #     # Return the results as the recursive iteration is now complete.
        # else:
        # TODO Break if required_models cannot be composed and needs to be provided by the user.
        # This means that the model inside the top_level required model also has a required model that should be
        # inside the recursive netlist and we need to find it. We iterate over each of the required model names to
        # see if they match our active component name.
        for required_model_name_i in required_models:
            # Appends required_models_i from subcomponent to the required_models input based on the measurement provided.

            try:
                required_models_i = sax.get_required_circuit_models(
                    recursive_netlist[required_model_name_i],
                    # TODO make this recursive so it can search inside? This will never have to be 2D as all measurement
                    #  outside.
                    models={**models, **model_composition_mapping},
                )  # eg. ["straight_heater_metal_s_ad3c1693"]
            except Exception as e:
                required_models_i = []
                print(e)

            # Check if required_model_name_i already composed.

            # Check that the model composition mapping has not already fulfilled this model.
            if len(required_models_i) != 0:
                if required_model_name_i in model_composition_mapping:
                    required_models.remove(required_model_name_i)
                else:
                    required_models.extend(required_models_i)
                    model_composition_mapping[required_model_name_i] = required_models_i
            elif len(required_models_i) == 0:
                # Remove from ``required_models`` to complete the recursion
                required_models.remove(required_model_name_i)

            # Get the corresponding instances of this model at this level of recursion.
            # Implement a function that matches all the potential corresponding matched instances on the top_level
            instance_composition_mapping_i = get_component_instances(
                recursive_netlist=recursive_netlist,
                top_level_prefix=top_level_instance_name,
                component_name_prefix=required_model_name_i,
            )  # {'mzi_214beef3': ['mzi_1', 'mzi_5']}
            instance_composition_mapping.update(instance_composition_mapping_i)

            # This model is now at a particular level of recursion, let's check if this is the model we want in the
            # required composed measurement.
            for required_model_name_i_i in required_models_i:
                if required_model_name_i_i.startswith(target_component_prefix):
                    # Yes, this is the model we want. Can we compose the instance location?
                    target_component_mapping.update(
                        {required_model_name_i_i: required_model_name_i}
                    )
                    # This means we need to check whether the components is our matched component, and if not,
                    # then we need to check if this other required component recursively also requires our active
                    # component. Implement the search again recursively from the unmatched components.

            # If the target_component has the corresponding mapping in the recursive_netlist then we can access the
            # lowest component element
            if required_model_name_i.startswith(target_component_prefix):
                if required_model_name_i in target_component_mapping:
                    instance_composition_mapping_i = get_component_instances(
                        recursive_netlist=recursive_netlist,
                        top_level_prefix=target_component_mapping[
                            required_model_name_i
                        ],
                        component_name_prefix=required_model_name_i,
                    )  # {'mzi_214beef3': ['mzi_1', 'mzi_5']}
                    instance_composition_mapping.update(instance_composition_mapping_i)

                # Assuming this always occurs at this highest level of hierarchy
                target_component_mapping.update(
                    {required_model_name_i: top_level_instance_name}
                )

        i += 1

    return (
        model_composition_mapping,
        instance_composition_mapping,
        target_component_mapping,
    )


def get_component_instances(
    recursive_netlist: dict,
    top_level_prefix: str,
    component_name_prefix: str,
):
    """
    Returns a dictionary of all instances of a given component in a recursive netlist.

     Args:
        recursive_netlist (dict): The hierarchical netlist dictionary.
        top_level_prefix (str): The prefix of the top-level instance to search under.
        component_name_prefix (str): The prefix of the component instances to find.

     Returns:
        dict: A dictionary mapping the component prefix to a list of instance names that match the prefix.
    """
    import sax

    # TODO interim function until Floris merges.
    recursive_netlist_sax = sax.netlist(recursive_netlist)
    instance_names = []
    recursive_netlist_root = recursive_netlist_sax.dict()["__root__"]
    top_level_prefix = get_netlist_instances_by_prefix(
        recursive_netlist, instance_prefix=top_level_prefix
    )  # Should only be one in a netlist-to-digraph. Can always be very specified.
    for key in recursive_netlist_root[top_level_prefix]["instances"]:
        if recursive_netlist_root[top_level_prefix]["instances"][key][
            "component"
        ].startswith(component_name_prefix):
            # Note priority encoding on match.
            instance_names.append(key)
    return {component_name_prefix: instance_names}


def get_netlist_instances_by_prefix(
    recursive_netlist: dict,
    instance_prefix: str,
) -> str:
    """
    Returns a list of all instances with a given prefix in a recursive netlist.

    Args:
        recursive_netlist (dict): The hierarchical netlist dictionary.
        instance_prefix (str): The prefix to search for within the netlist instances.

    Returns:
        str: The name of the instance that matches the given prefix.

    Raises:
        ValueError: If no instance or more than one instance matches the given prefix.

    """
    import sax

    # TODO interim function until Floris merges.
    recursive_netlist = sax.netlist(recursive_netlist)
    recursive_netlist_root = recursive_netlist.dict()["__root__"]
    result = []
    for key in recursive_netlist_root.keys():
        if key.startswith(instance_prefix):
            result.append(key)

    if len(result) == 1:
        return result[0]
    elif len(result) == 0:
        raise ValueError(
            "No instances with prefix: "
            + instance_prefix
            + " found. These are the available instances: "
            + str(recursive_netlist_root.keys())
        )
    else:
        print(len(result))
        raise ValueError(
            "More than one instance with prefix: "
            + instance_prefix
            + "found. These are the matched "
            "instances: " + str(result)
        )


def get_matched_model_recursive_netlist_instances(
    recursive_netlist: dict,
    top_level_instance_prefix: str,
    target_component_prefix: str,
    models: Optional[dict] = None,
    custom_subcomponent_instance: Optional[
        str
    ] = "sxt",  # For backwards compatibility TODO properly sort this out.
) -> list[tuple]:
    """
    This function returns an active component list with a tuple mapping of the location of the active component
    within the recursive netlist and corresponding model. It will recursively look within a netlist to locate what
    measurement use a particular component model. At each stage of recursion, it will compose a list of the elements that
    implement this matching model in order to relate the model to the instance, and hence the netlist address of the
    component that needs to be updated in order to functionally implement the model.

    It takes in as a set of parameters the recursive_netlist generated by a ``gdsfactory`` netlist implementation.

    Returns a list of tuples, that correspond to the phases applied with the corresponding component paths at
    multiple levels of recursion. eg. [("component_lattice_gener_fb8c4da8", "mzi_1", "sxt"),
    ("component_lattice_gener_fb8c4da8", "mzi_5", "sxt")] and these are our keys to our sax circuit decomposition.

    Args:
        recursive_netlist (dict): The hierarchical netlist dictionary.
        top_level_instance_prefix (str): The prefix of the top-level instance to search under.
        target_component_prefix (str): The prefix of the target component to find.
        models (Optional[dict]): A dictionary of measurement to aid in the recursion. Defaults to None.
        custom_subcomponent_instance (Optional[str]): The instance name for subcomponents, used for backwards compatibility.

    Returns:
        list[tuple]: A list of tuples, each containing the hierarchical path to the matched component instances.
        Each tuple has the form (parent_component, target_instance, custom_subcomponent_instance).

    """
    import sax

    matched_instance_list = []
    if models is None:
        models = get_default_models()

    # We need to input the top-level instance.
    top_level_instance_name = get_netlist_instances_by_prefix(
        recursive_netlist=recursive_netlist,
        instance_prefix=top_level_instance_prefix,
    )

    # We need to input the prefix of the component of the straight metal heater.
    top_level_required_models = sax.get_required_circuit_models(
        recursive_netlist[top_level_instance_name],
        models=models,
    )

    (
        model_composition_mapping,
        instance_composition_mapping,
        target_component_mapping,
    ) = compose_recursive_instance_location(
        recursive_netlist=recursive_netlist,
        top_level_instance_name=top_level_instance_name,
        required_models=top_level_required_models.copy(),
        target_component_prefix=target_component_prefix,
        models=models,
    )

    # Now we have the raw files that creates the mapping of the components-to-instances, in order to create the
    # corresponding instance address indexes that we can use to control our matching element parameters.
    # Currently this onloy assumes up to three levels of hierarchy, TODO make recursive
    if len(target_component_mapping.keys()) != 0:
        # This means that the target_component has been mapped to a parent recursive_netlist cell.
        for target_component_name_i in target_component_mapping.keys():
            if target_component_name_i.startswith(target_component_prefix):
                recursive_parent_component_i = target_component_mapping[
                    target_component_name_i
                ]  # Get the parent cell.

                for target_instances_i in instance_composition_mapping[
                    target_component_name_i
                ]:
                    matched_instance_list.append(
                        (
                            recursive_parent_component_i,
                            target_instances_i,
                            custom_subcomponent_instance,
                        )
                    )
            else:
                # Tells us the name of our component
                recursive_parent_component_i = target_component_mapping[
                    target_component_name_i
                ]  # Get the parent cell.
                for parent_instances_i in instance_composition_mapping[
                    recursive_parent_component_i
                ]:
                    # TODO check parent_instances_i not in target_component_mapping to increase hierarchy.
                    # TODO implement as another recursive problem. NMP right now.
                    for target_instances_i in instance_composition_mapping[
                        target_component_name_i
                    ]:
                        matched_instance_list.append(
                            (
                                top_level_instance_name,
                                parent_instances_i,
                                target_instances_i,
                            )
                        )

    return matched_instance_list
