from typing import Final

import torch
from mace.modules.models import MACE
from mace.modules.utils import get_edge_vectors_and_lengths
from e3nn.util.jit import compile_mode

from franken.data import Configuration


@compile_mode("script")
class FrankenMACE(torch.nn.Module):
    interaction_block: Final[int]

    def __init__(self, base_model: MACE, interaction_block, gnn_backbone_id):
        super().__init__()
        self.base_model = base_model
        self.gnn_backbone_id = gnn_backbone_id
        self.interaction_block = interaction_block
        self.interactions = self.base_model.interactions[: self.interaction_block]
        self.products = self.base_model.products[: self.interaction_block]
        self.atomic_numbers = self.base_model.atomic_numbers

    def init_args(self):
        return {
            "gnn_backbone_id": self.gnn_backbone_id,
            "interaction_block": self.interaction_block,
        }

    def descriptors(self, data: Configuration) -> torch.Tensor:
        if self.interaction_block > len(self.base_model.interactions):
            raise ValueError(
                f"This model has {len(self.base_model.interactions)} gnn layers, while descriptors have been required for the {self.interaction_block} layer"
            )
        # assert on local variables to make torchscript happy
        edge_index = data.edge_index
        shifts = data.shifts
        node_attrs = data.node_attrs
        assert edge_index is not None
        assert shifts is not None
        assert node_attrs is not None
        # Embeddings
        node_feats = self.base_model.node_embedding(node_attrs)
        vectors, lengths = get_edge_vectors_and_lengths(
            positions=data.atom_pos,
            edge_index=edge_index,
            shifts=shifts,
        )
        edge_attrs = self.base_model.spherical_harmonics(vectors)
        edge_feats = self.base_model.radial_embedding(
            lengths, node_attrs, edge_index, self.base_model.atomic_numbers
        )

        node_feats_list = []
        for interaction, product in zip(self.interactions, self.products):
            node_feats, sc = interaction(
                node_attrs=node_attrs,
                node_feats=node_feats,
                edge_attrs=edge_attrs,
                edge_feats=edge_feats,
                edge_index=edge_index,
            )

            node_feats = product(node_feats=node_feats, sc=sc, node_attrs=node_attrs)
            # Extract only scalars. Use `irreps_out` attribute to figure out which features correspond to scalars.
            # irreps_out is an `Irreps` object: a 2-tuple of multiplier and `Irrep` objects.
            # Tuple[Tuple[int, Tuple[int, int]], Tuple[int, Tuple[int, int]]]
            # The `Irrep` object is a tuple consisting of parameters `l` and `p`.
            # The scalar irrep is the first in `irreps_out`. Its dimension is computed
            # as `mul * ir.dim` where `ir.dim == 2 * ir.l  + 1`
            # Note this is equivalent code, which does not support TorchScript.
            # invariant_slices = product.linear.irreps_out.slices()[0]
            irreps = product.linear.irreps_out
            invariant_slices = slice(0, irreps[0][0] * (2 * irreps[0][1][0] + 1))
            node_feats_list.append(node_feats[..., invariant_slices])
        return torch.cat(node_feats_list, dim=-1)

    def num_params(self) -> int:
        return sum(p.numel() for p in self.base_model.parameters())

    def feature_dim(self):
        return (
            self.interaction_block
            * self.base_model.node_embedding.linear.irreps_out.count("0e")
        )

    @staticmethod
    def load_from_checkpoint(
        trainer_ckpt, gnn_backbone_id: str, interaction_block: int, map_location=None
    ) -> "FrankenMACE":
        mace = torch.load(
            trainer_ckpt, map_location=map_location, weights_only=False
        ).to(dtype=torch.float32)
        return FrankenMACE(
            base_model=mace,
            gnn_backbone_id=gnn_backbone_id,
            interaction_block=interaction_block,
        )
