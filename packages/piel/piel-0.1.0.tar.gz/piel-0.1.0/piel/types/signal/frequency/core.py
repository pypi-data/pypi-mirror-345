"""
One of the main complexities of defining frequency domain models is the dimensionality difference between
photonic and radio-frequency s-parameter responses. Whilst, in a way, it's similar - it can also be different.

One interesting difference is possibly related to the number of higher number S matrices in photonics, which also exist in RF.
For example, in a 4-port 2x2 MMI, we are looking into the transmission and back reflection of one port with N connection, in this case 2 output connection.
This kind of means that standard 2-port devices we probe using VNAs, still can probe N modes, but it has to be higher-dimensionally post-multiple-measurements constructed. So clearly, the way we probe photonics and electronics in a way is inherently different.

When we use an array of VGAs to measure PIC connection, we can measure averaged optical power which is a spectrum to scalar conversion.
I guess it's the equivalent of an RF powermeter too? But I feel the infrastructure is more multi-port in photonics than RF broadly,
or at least at a more accessible price.

So when we define a given static-frequency transformation across a circuit, in photonics it's clearer to define this at multiple connection.
The measurement we would do with a VNA or OSA, would give us a set of network transformations at multiple frequencies.

However, if we want to create static frequency transmission models, we need to think about an individual frequency.
So ultimately, in the way we represent network transformations, there is an inherent map relationship at a given frequency.
And at that given frequency we can create a full network transmission model. In this sense, I think the fundamental
data structure has to be a dictionary, of dictionaries to represent ``port -> transmission``  responses and this is
what sax does so well in embedding this into network machine learning in this format.

A higher dimensional mapping is ``state -> port -> transmission`` where the state can correspond to a given input mode,
frequency or power yet the physical transmission mapping is equivalent. As such, this is the data structure we implement.
However, this has performance caveats and I believe computation onto this data structure should be optimised.

Possibly, this is why when we are measuring an equivalent spectrum we might want to treat the network as a set of arrays
for computational speedup. So inherently, it could be argued, for reasonable speed there might need to be transformations
in between these data types depending on whether optimizing network multi-port responses like photonics, or spectrum analysis.
It is not exactly clear to me the most fundamental way to implement this that does not have inherent computational cost.
"""

from __future__ import annotations
from __future__ import annotations
from piel.types.core import ArrayTypes, NumericalTypes
from piel.types.connectivity.abstract import Instance
from piel.types.units import Unit, Hz, dBm, degree
from piel.base.signal.frequency.transmission import get_phasor_length
from pydantic import model_validator


class Phasor(Instance):
    """
    Contains magnitude and phase frequency response information.
    Can represent both an array or individual response. Equivalent to a single-frequency response.
    Contains a very clear notation to translate with a complex number and this term.

    .. math::

         Ae^{i(\omega t+\theta)}
    """

    magnitude: NumericalTypes | ArrayTypes
    """
    Should represent an absolute value real number.
    """

    phase: NumericalTypes | ArrayTypes
    """
    Should represent an absolute value real number.
    """

    frequency: NumericalTypes | ArrayTypes
    """
    Should represent an absolute value real number.
    """

    frequency_unit: Unit = Hz
    phase_unit: Unit = degree
    magnitude_unit: Unit = dBm

    @property
    def data(self):
        # Create a dictionary with the scalar metrics
        data = {
            "label": [
                f"magnitude_{self.magnitude_unit.shorthand}",
                f"phase_{self.phase_unit.shorthand}",
                f"frequency_{self.frequency_unit.shorthand}",
            ],
            "value": [self.magnitude, self.phase, self.frequency],
        }
        return data

    @property
    def table(self):
        import pandas as pd

        # Convert to a pandas DataFrame
        df = pd.DataFrame(self.data)
        return df

    @model_validator(mode="after")
    def check_lengths_consistency(cls, model):
        """
        Validates that the lengths of magnitude, phase, and frequency are exactly the same.
        All must have the same length, regardless of being scalar or arrays.
        """
        mag_length = get_phasor_length(model.magnitude)
        phase_length = get_phasor_length(model.phase)
        freq_length = get_phasor_length(model.frequency)

        if mag_length != phase_length or mag_length != freq_length:
            raise ValueError(
                f"Length mismatch among magnitude ({mag_length}), phase ({phase_length}), "
                f"and frequency ({freq_length}). All must be the same length."
            )

        return model
