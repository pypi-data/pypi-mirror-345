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
"""Xmanager command-line interface."""

import errno
import importlib
import os
import sys

from absl import app

_DEFAULT_ZONE = 'us-west1-b'
_DEFAULT_CLUSTER_NAME = 'xmanager-via-caliban'


def main(argv):
  if len(argv) < 3:
    raise app.UsageError('There must be at least 2 command-line arguments')
  cmd = argv[1]
  if cmd == 'launch':
    launch_script = argv[2]
    if not os.path.exists(launch_script):
      raise OSError(errno.ENOENT, f'File not found: {launch_script}')
    sys.path.insert(0, os.path.abspath(os.path.dirname(launch_script)))
    launch_module, _ = os.path.splitext(os.path.basename(launch_script))
    m = importlib.import_module(launch_module)
    sys.path.pop(0)
    argv = [
        launch_script,
        '--xm_launch_script={}'.format(launch_script),
    ] + argv[3:]
    app.run(m.main, argv=argv)
  elif cmd == 'cluster':
    caliban_gke = importlib.import_module('caliban.platform.gke.cli')
    caliban_gke_types = importlib.import_module('caliban.platform.gke.types')
    subcmd = argv[2]
    args = {
        'dry_run': False,
        'cluster_name': _DEFAULT_CLUSTER_NAME,
        'zone': _DEFAULT_ZONE,
        'release_channel': caliban_gke_types.ReleaseChannel.REGULAR,
        'single_zone': True,
    }
    if subcmd == 'create':
      caliban_gke._cluster_create(args)  # pylint: disable=protected-access
    elif subcmd == 'delete':
      caliban_gke._cluster_delete(args)  # pylint: disable=protected-access
    else:
      raise app.UsageError(
          f'Subcommand `{cmd} {subcmd}` is not a supported subcommand'
      )
  else:
    raise app.UsageError(f'Command `{cmd}` is not a supported command')


def entrypoint():
  app.run(main)


if __name__ == '__main__':
  app.run(main)
