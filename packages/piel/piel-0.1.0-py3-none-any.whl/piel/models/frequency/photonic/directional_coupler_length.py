"""
Translated from https://github.com/flaport/sax or https://github.com/flaport/photontorch/tree/master
"""


def directional_coupler_with_length(
    length=1e-5, coupling=0.5, loss=0, neff=2.34, wl0=1.55e-6, ng=3.40, phase=0
):
    import jax.numpy as jnp
    import sax

    kappa = coupling**0.5
    tau = (1 - coupling) ** 0.5
    loss = 10 ** (-loss * length / 20)  # factor 20 bc amplitudes, not intensities.
    cos_phase = jnp.cos(phase)
    sin_phase = jnp.sin(phase)
    sdict = sax.reciprocal(
        {
            ("port0", "port1"): tau * loss * cos_phase,
            ("port0", "port2"): -kappa * loss * sin_phase,
            ("port1", "port3"): -kappa * loss * sin_phase,
            ("port2", "port3"): tau * loss * cos_phase,
        }
    )
    return sdict
