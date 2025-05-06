# Copyright 2025 Advanced Micro Devices, Inc.
#
# Licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

"""
Specifications describing how
"""

from iree.turbine.aot import DeviceTensorTrait, ExternalTensorTrait
from sharktank.types import (
    DefaultPrimitiveTensor,
    PrimitiveTensor,
    ReplicatedTensor,
    ShardedTensor,
    Theta,
)


from typing import Tuple


def pipeline_parallelize_theta(
    theta: Theta, pipeline_parallelism_size: int
) -> tuple[tuple[int, ...], ...]:
    """
    Pipeline parallelize theta for LLM.
    Both DeepSeek and Llama.
    """

    def parallelize_in_place(
        block_data: dict[str, ShardedTensor | PrimitiveTensor],
        new_devices: Tuple[int, ...],
    ) -> None:
        """
        Parallelize the block data in place.
        """
        assert len(block_data) == 1
        key = list(block_data.keys())[0]
        tensor = block_data[key]

        (old_shards, old_devices) = (
            ([tensor], (0,))
            if isinstance(tensor, PrimitiveTensor)
            else (tensor.shards, tensor.devices)
        )
        new_shards = ShardedTensor.move_shards_to_new_devices(
            old_shards, old_devices=old_devices, new_devices=new_devices
        )

        for i, (old_shard, new_shard) in enumerate(zip(old_shards, new_shards)):
            DeviceTensorTrait(new_devices[i]).set(new_shard._data)
            if old_tensor_trait := ExternalTensorTrait.get(old_shard._data):
                ExternalTensorTrait(
                    old_tensor_trait.external_scope,
                    old_tensor_trait.external_name,
                ).set(new_shard._data)

        block_data[key] = (
            ReplicatedTensor(ts=new_shards, name=tensor.name, devices=new_devices)
            if isinstance(tensor, PrimitiveTensor)
            else tensor.clone(ts=new_shards, devices=new_devices)
        )

    _t = theta.tensor("token_embd")["weight"]
    shard_count = 1 if isinstance(_t, DefaultPrimitiveTensor) else _t.shard_count
    num_blocks = len(theta.tensor("blk"))

    block_to_device_lookup = []
    block_indices = sorted(theta.tensor("blk").keys(), key=lambda item: int(item))
    assert (
        bi == i for i, bi in enumerate(block_indices)
    ), "Blocks assumed to be numbered contiguously from [0, N-1]"
    for blk_idx in block_indices:
        pp_group = int(int(blk_idx) * pipeline_parallelism_size / num_blocks)
        zero_4_group = shard_count * pp_group
        devices = tuple(i + zero_4_group for i in range(shard_count))
        block_to_device_lookup.append(devices)

        block_data = theta.tensor("blk", blk_idx)
        for t_name in block_data.keys():
            parallelize_in_place(block_data[t_name], devices)

    parallelize_in_place(theta.tensor("token_embd"), block_to_device_lookup[0])
    parallelize_in_place(theta.tensor("output_norm"), block_to_device_lookup[-1])
    parallelize_in_place(theta.tensor("output"), block_to_device_lookup[-1])

    return tuple(block_to_device_lookup)
