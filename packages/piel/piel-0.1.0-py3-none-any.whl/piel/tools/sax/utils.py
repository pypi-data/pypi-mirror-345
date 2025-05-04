"""
This file provides a set of utilities that allow much easier integration between `sax` and the relevant tools that we use.
"""

import jax.numpy as jnp
from ..gdsfactory.netlist import get_matched_ports_tuple_index
from ...utils import round_complex_array
from ...types import SParameterMatrixTuple
from typing import Optional, Any  # NOQA : F401


def get_sdense_ports_index(input_ports_order: tuple, all_ports_index: dict) -> dict:
    """
    This function returns the connection index of the sax dense S-parameter matrix.

    Given that the order of the iteration is provided by the user, the dictionary keys will also be ordered
    accordingly when iterating over them. This requires the user to provide a set of ordered.

    TODO verify reasonable iteration order.

    .. code-block:: python

        # The input_ports_order can be a tuple of tuples that contain the index and port name. Eg.
        input_ports_order = ((0, "in_o_0"), (5, "in_o_1"), (6, "in_o_2"), (7, "in_o_3"))
        # The all_ports_index is a dictionary of the connection index. Eg.
        all_ports_index = {
            "in_o_0": 0,
            "out_o_0": 1,
            "out_o_1": 2,
            "out_o_2": 3,
            "out_o_3": 4,
            "in_o_1": 5,
            "in_o_2": 6,
            "in_o_3": 7,
        }
        # Output
        {"in_o_0": 0, "in_o_1": 5, "in_o_2": 6, "in_o_3": 7}

    Args:
        input_ports_order (tuple): The connection order tuple. Can be a tuple of tuples that contain the index and port name.
        all_ports_index (dict): The connection index dictionary.

    Returns:
        tuple: The ordered input connection index tuple.
    """
    # TODO look into jnp.at method https://github.com/flaport/sax/blob/a87c3bf8c792dc227779e5d010627897f4cd8278/sax/typing_.py#L355
    input_ports_index = {key: all_ports_index[key] for key in input_ports_order}
    return input_ports_index


def sax_to_s_parameters_standard_matrix(
    sax_input: Any,
    input_ports_order: tuple[str] | None = None,
    round_int: bool | None = None,
    *args,
    **kwargs,
) -> SParameterMatrixTuple:
    """
    A ``sax`` S-parameter SDict is provided as a dictionary of tuples with (port0, port1) as the key. This
    determines the direction of the scattering relationship. It means that the number of terms in an S-parameter
    matrix is the number of connection squared.

    In order to generalise, this function returns both the S-parameter matrices and the indexing connection based on the
    amount provided. In terms of computational speed, we definitely would like this function to be algorithmically
    very fast. For now, I will write a simple python implementation and optimise in the future.

    It is possible to see the `sax` SDense notation equivalence here:
    https://flaport.github.io/sax/nbs/08_backends.html

    .. code-block:: python

        import jax.numpy as jnp
        from sax.core import SDense

        # Directional coupler SDense representation
        dc_sdense: SDense = (
            jnp.array([[0, 0, τ, κ], [0, 0, κ, τ], [τ, κ, 0, 0], [κ, τ, 0, 0]]),
            {"in0": 0, "in1": 1, "out0": 2, "out1": 3},
        )


        # Directional coupler SDict representation
        # Taken from https://flaport.github.io/sax/nbs/05_models.html
        def coupler(*, coupling: float = 0.5) -> SDict:
            kappa = coupling**0.5
            tau = (1 - coupling) ** 0.5
            sdict = reciprocal(
                {
                    ("in0", "out0"): tau,
                    ("in0", "out1"): 1j * kappa,
                    ("in1", "out0"): 1j * kappa,
                    ("in1", "out1"): tau,
                }
            )
            return sdict

    If we were to relate the mapping accordingly based on the connection indexes, a S-Parameter matrix in the form of
    :math:`S_{(output,i),(input,i)}` would be:

    .. math::

        S = \\begin{bmatrix}
                S_{00} & S_{10} \\\\
                S_{01} & S_{11} \\\\
            \\end{bmatrix} =
            \\begin{bmatrix}
            \\tau & j \\kappa \\\\
            j \\kappa & \\tau \\\\
            \\end{bmatrix}

    Note that the standard S-parameter and hence unitary representation is in the form of:

    .. math::

        S = \\begin{bmatrix}
                S_{00} & S_{01} \\\\
                S_{10} & S_{11} \\\\
            \\end{bmatrix}


    .. math::

        \\begin{bmatrix}
            b_{1} \\\\
            \\vdots \\\\
            b_{n}
        \\end{bmatrix}
        =
        \\begin{bmatrix}
            S_{11} & \\dots & S_{1n} \\\\
            \\vdots & \\ddots & \\vdots \\\\
            S_{n1} & \\dots & S_{nn}
        \\end{bmatrix}
        \\begin{bmatrix}
            a_{1} \\\\
            \\vdots \\\\
            a_{n}
        \\end{bmatrix}

    TODO check with Floris, does this mean we need to transpose the matrix?
    TODO document round_int

    Args:
        sax_input (sax.SType): The sax S-parameter dictionary.
        input_ports_order (tuple): The connection order tuple containing the names and order of the input connection.
        round_int (bool): Whether to round the complex numbers to integers.

    Returns:
        tuple: The S-parameter matrix and the input connection index tuple in the standard S-parameter notation.
    """
    import sax

    dense_s_parameter_matrix, dense_s_parameter_index = sax.sdense(sax_input)
    # print(dense_s_parameter_index)
    all_ports_list = dense_s_parameter_index.keys()
    # Now we get the indexes of the input connection that we care about to restructure the dense matrix with the columns
    # we care about.
    if input_ports_order is not None:
        output_ports_order = tuple(set(all_ports_list) - set(input_ports_order))
        (
            input_ports_index_tuple_order,
            input_matched_ports_name_tuple_order,
        ) = get_matched_ports_tuple_index(
            ports_index=dense_s_parameter_index,
            selected_ports_tuple=input_ports_order,
            sorting_algorithm="selected_ports",
        )
        (
            output_ports_index_tuple_order,
            output_matched_ports_name_tuple_order,
        ) = get_matched_ports_tuple_index(
            ports_index=dense_s_parameter_index,
            selected_ports_tuple=output_ports_order,
            sorting_algorithm="selected_ports",
        )
    else:
        (
            input_ports_index_tuple_order,
            input_matched_ports_name_tuple_order,
        ) = get_matched_ports_tuple_index(
            ports_index=dense_s_parameter_index, prefix="in"
        )
        (
            output_ports_index_tuple_order,
            output_matched_ports_name_tuple_order,
        ) = get_matched_ports_tuple_index(
            ports_index=dense_s_parameter_index, prefix="out"
        )

    output_ports_index_tuple_order_jax = jnp.asarray(output_ports_index_tuple_order)
    input_ports_index_tuple_order_jax = jnp.asarray(input_ports_index_tuple_order)
    # We now select the SDense columns that we care about.
    try:
        s_parameters_standard_matrix = dense_s_parameter_matrix.at[
            output_ports_index_tuple_order_jax
        ].get()
    except TypeError as e:
        print("sax_input: " + str(sax_input))
        print("all_ports_list: " + str(all_ports_list))
        print("output_ports_index_tuple_order: " + str(output_ports_index_tuple_order))
        raise TypeError(
            "Verify your network composition contains `out` keywords. This can be caused by the network topology."
        ) from e
    s_parameters_standard_matrix = s_parameters_standard_matrix.at[
        :, input_ports_index_tuple_order_jax
    ].get()
    # Now we select the SDense rows that we care about after transposing the matrix.

    if round_int:
        s_parameters_standard_matrix = round_complex_array(
            s_parameters_standard_matrix, **kwargs
        )

    value = s_parameters_standard_matrix, input_matched_ports_name_tuple_order
    return value


snet = sax_to_s_parameters_standard_matrix
