__all__ = ["awg2m2"]


def awg2m2(awg: int) -> float:
    """
    Converts an AWG value to meters squared.

    Reference: https://en.wikipedia.org/wiki/American_wire_gauge

    Args:
        awg (ing): AWG value.

    Returns:
        float: Cross sectional area in meters squared.
    """
    return ((0.127) * (92 ** ((36 - awg) / 39))) * 1e-3
