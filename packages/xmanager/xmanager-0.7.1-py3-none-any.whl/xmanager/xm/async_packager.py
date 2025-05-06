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
"""An utility to batch Packageables together and build them in one go."""

import asyncio
import concurrent.futures as concurrent_futures
import threading
from typing import Awaitable, Callable, Sequence, TypeVar

from xmanager.xm import job_blocks


class PackageHasNotBeenCalledError(RuntimeError):
  """Access to package_async() awaitable prior to calling .package()."""


Awaited = TypeVar('Awaited')


class PicklableAwaitableImpl:
  """Awaitable type with known value which can be pickled."""

  def __init__(
      self,
      get_future: Callable[
          [], asyncio.Future[Awaited] | concurrent_futures.Future[Awaited]
      ],
  ):
    self._get_future = get_future

  def __await__(self):
    return asyncio.wrap_future(self._get_future()).__await__()

  def __reduce__(self):
    return _return_awaited, (self._get_future().result(),)


def _return_awaited(
    awaited: Awaited,
) -> Awaitable[Awaited]:
  """Returns a picklable awaitable for an already known value."""

  def get_future() -> asyncio.Future[Awaited]:
    future = asyncio.Future()
    future.set_result(awaited)
    return future

  return PicklableAwaitableImpl(get_future)


class AsyncPackager:
  """An utility to batch Packageables together and build them in one go.

  Attributes:
    _lock: A Lock() object used to make the class threadsafe.
    _package_batch: A function which packages a batch of Packageables.
    _packageables: Packageables queued to be packaged.
    _futures: Corresponding futures where packaging results should be written.
  """

  def __init__(
      self,
      package_batch: Callable[
          [Sequence[job_blocks.Packageable]], Sequence[job_blocks.Executable]
      ],
  ) -> None:
    """Creates the async packager.

    Args:
      package_batch: A function which packages a batch of Packageables.
    """
    super().__init__()
    self._lock = threading.Lock()
    self._package_batch = package_batch
    self._packageables = []
    self._futures = []

  def add(
      self, packageable: job_blocks.Packageable
  ) -> Awaitable[job_blocks.Executable]:
    """Adds new packageable to the batch."""
    with self._lock:
      future = concurrent_futures.Future()
      self._packageables.append(packageable)
      self._futures.append(future)

    def check_is_packaged() -> None:
      with self._lock:
        if packageable in self._packageables:
          raise PackageHasNotBeenCalledError(
              '.package() must be called before awaiting on the packaging '
              'result'
          )

    def get_future() -> concurrent_futures.Future[job_blocks.Executable]:
      check_is_packaged()
      return future

    return PicklableAwaitableImpl(get_future)

  def package(
      self, extra_packageables: Sequence[job_blocks.Packageable] = ()
  ) -> Sequence[job_blocks.Executable]:
    """Triggers the packaging of previously added packageables.

    Args:
      extra_packageables: An explicit sequence of extra packageables items to
        package synchronously.

    Returns:
      The list of executables corresponding to `extra_packageables`.
    """
    with self._lock:
      packageables = self._packageables + list(extra_packageables)
      futures = self._futures
      self._packageables = []
      self._futures = []

    if not packageables:
      return []

    try:
      executables = self._package_batch(packageables)
      for executable, future in zip(executables, futures):
        future.set_result(executable)
      return executables[len(futures) :]
    except Exception as e:
      for future in futures:
        future.set_exception(e)
      raise
