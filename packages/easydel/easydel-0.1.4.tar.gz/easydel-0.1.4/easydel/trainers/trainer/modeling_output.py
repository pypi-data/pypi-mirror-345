# Copyright 2023 The EASYDEL Author @erfanzar (Erfan Zare Chavoshi).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import typing as tp

import jax
from eformer.pytree import auto_pytree

if tp.TYPE_CHECKING:
	from easydel.infra.base_state import EasyDeLState
else:
	EasyDeLState = tp.Any


@auto_pytree
class TrainerOutput:
	state: EasyDeLState
	mesh: tp.Optional[jax.sharding.Mesh]
	checkpoint_manager: tp.Any
	gather_fns: tp.Optional[
		tp.Any | tp.Mapping[str, tp.Callable] | tp.Dict[str, tp.Callable]
	] = None
	shard_fns: tp.Optional[
		tp.Any | tp.Mapping[str, tp.Callable] | tp.Dict[str, tp.Callable]
	] = None
	last_save_file_name: tp.Optional[str] = None
	checkpoint_path: tp.Optional[str] = None
