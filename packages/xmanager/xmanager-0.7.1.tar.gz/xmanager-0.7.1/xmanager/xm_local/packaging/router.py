# Copyright 2021 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Methods for routing packageables to appropriate packagers."""

import collections
from typing import Dict, List, Sequence, Tuple

from xmanager import xm
from xmanager.bazel import client as bazel_client
from xmanager.xm_local import executors
from xmanager.xm_local.packaging import bazel_tools
from xmanager.xm_local.packaging import cloud as cloud_packaging
from xmanager.xm_local.packaging import local as local_packaging


def _packaging_router(
    built_targets: bazel_tools.TargetOutputs, packageable: xm.Packageable
) -> xm.Executable:
  match packageable.executor_spec:
    case executors.VertexSpec():
      return cloud_packaging.package_cloud_executable(
          built_targets,
          packageable,
          packageable.executable_spec,
      )
    case executors.LocalSpec():
      return local_packaging.package_for_local_executor(
          built_targets,
          packageable,
          packageable.executable_spec,
      )
    case executors.KubernetesSpec():
      return cloud_packaging.package_cloud_executable(
          built_targets,
          packageable,
          packageable.executable_spec,
      )
    case _:
      raise TypeError(
          f'Unsupported executor specification: {packageable.executor_spec!r}. '
          f'Packageable: {packageable!r}'
      )


_ArgsToTargets = Dict[Tuple[str, ...], List[bazel_client.BazelTarget]]


def package(packageables: Sequence[xm.Packageable]) -> List[xm.Executable]:
  """Routes a packageable to an appropriate packaging mechanism."""
  built_targets: bazel_tools.TargetOutputs = {}
  bazel_targets = bazel_tools.collect_bazel_targets(packageables)

  if bazel_targets:
    bazel_service = bazel_tools.local_bazel_service()

    args_to_targets: _ArgsToTargets = collections.defaultdict(list)
    for target in bazel_targets:
      args_to_targets[target.bazel_args].append(target)
    for args, targets in args_to_targets.items():
      outputs = bazel_service.build_targets(
          labels=tuple(target.label for target in targets),
          bazel_args=args,
      )
      for target, output in zip(targets, outputs):
        built_targets[target] = output

  return [
      _packaging_router(built_targets, packageable)
      for packageable in packageables
  ]
