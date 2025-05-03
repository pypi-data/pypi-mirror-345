import logging

import torch


logger = logging.getLogger("franken")


def patch_e3nn():
    # NOTE:
    #  Patching should occur when doing training: it is necessary for `jvp` on the MACE model,
    #  but not during inference, when we only use `torch.autograd`. For inference, we may want
    #  to compile the model using `torch.jit` - and the patch interferes with the JIT, so we
    #  must disable it.

    # Ugly patch code. Need to replace a scripted function, but it's messy.
    import e3nn.o3._spherical_harmonics

    new_locals = {"Tensor": torch.Tensor}
    if not hasattr(e3nn.o3._spherical_harmonics._spherical_harmonics, "code"):
        # Either it has already been patched or it's a newer e3nn version
        # which doesn't need patching!
        return
    exec(e3nn.o3._spherical_harmonics._spherical_harmonics.code, None, new_locals)

    def _spherical_harmonics(
        lmax: int, x: torch.Tensor, y: torch.Tensor, z: torch.Tensor
    ) -> torch.Tensor:
        return new_locals["_spherical_harmonics"](torch.tensor(lmax), x, y, z)

    e3nn.o3._spherical_harmonics._spherical_harmonics = _spherical_harmonics
