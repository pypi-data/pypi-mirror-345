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

import asyncio
from concurrent import futures
import threading
import unittest

from xmanager import xm_mock
from xmanager.xm import core
from xmanager.xm import job_blocks
from xmanager.xm import utils


class TestError(RuntimeError):
  """Exception which can be used in tests below."""


async def failing_job_generator(work_unit: core.WorkUnit):
  raise TestError


class ApplyArgsTest(unittest.TestCase):

  def test_wrong_job_args(self):
    with self.assertRaises(ValueError):
      core._apply_args(
          job_blocks.Job(
              job_blocks.Executable(name=''), xm_mock.MockExecutor()
          ),
          {'abra': 'kadabra'},
      )

  def test_wrong_job_group_args(self):
    with self.assertRaises(ValueError):
      core._apply_args(
          job_blocks.JobGroup(
              learner=job_blocks.Job(
                  job_blocks.Executable(name=''), xm_mock.MockExecutor()
              )
          ),
          {'eval': {'args': {'batch_size': 32}}},
      )


class ExperimentTest(unittest.TestCase):

  def test_single_job_launch(self):
    experiment = xm_mock.MockExperiment()
    with experiment:
      job = job_blocks.Job(
          xm_mock.MockExecutable(), xm_mock.MockExecutor(), args={}, name='name'
      )
      experiment.add(job)

    self.assertEqual(experiment.launched_jobs, [job])

  def test_job_group_launch(self):
    experiment = xm_mock.MockExperiment()
    with experiment:
      foo_job = job_blocks.Job(
          xm_mock.MockExecutable(),
          xm_mock.MockExecutor(),
          args={'foo': 1},
          name='1',
      )
      bar_job = job_blocks.Job(
          xm_mock.MockExecutable(),
          xm_mock.MockExecutor(),
          args={'bar': 2},
          name='2',
      )
      experiment.add(job_blocks.JobGroup(foo=foo_job, bar=bar_job))

    self.assertEqual(experiment.launched_jobs, [foo_job, bar_job])

  def test_job_generator_launch(self):
    experiment = xm_mock.MockExperiment()
    with experiment:
      job = job_blocks.Job(
          xm_mock.MockExecutable(), xm_mock.MockExecutor(), args={}, name='name'
      )

      async def job_generator(work_unit: core.WorkUnit, use_magic: bool):
        self.assertEqual(use_magic, True)
        work_unit.add(job)

      experiment.add(job_generator, args={'use_magic': True})

    self.assertEqual(experiment.launched_jobs, [job])
    self.assertEqual(experiment.launched_jobs_args, [{'use_magic': True}])

  def test_job_generator_raises(self):
    experiment = xm_mock.MockExperiment()
    with self.assertRaises(TestError):
      with experiment:
        experiment.add(failing_job_generator)

  def test_non_async_job_generator_raises_user_friendly_exception(self):
    with self.assertRaisesRegex(ValueError, '.* generator must be an async .*'):
      with xm_mock.MockExperiment() as experiment:

        def job_generator(work_unit: core.WorkUnit):
          del work_unit

        experiment.add(job_generator)

  def test_auxiliary_unit_job(self):
    experiment = xm_mock.MockExperiment()
    with experiment:
      job = job_blocks.Job(
          xm_mock.MockExecutable(), xm_mock.MockExecutor(), args={}, name='name'
      )
      experiment.add(core.AuxiliaryUnitJob(job, termination_delay_secs=600))

    self.assertEqual(len(experiment.auxiliary_units), 1)

  def test_auxiliary_unit_job_generator(self):
    experiment = xm_mock.MockExperiment()
    with experiment:

      async def make_job(aux_unit: core.ExperimentUnit):
        aux_unit.add(
            job_blocks.Job(
                xm_mock.MockExecutable(),
                xm_mock.MockExecutor(),
                args={},
                name='name',
            )
        )

      experiment.add(
          core.AuxiliaryUnitJob(make_job, termination_delay_secs=600)
      )

    self.assertEqual(len(experiment.auxiliary_units), 1)

  def test_launch_with_args(self):
    experiment = xm_mock.MockExperiment()
    with experiment:
      experiment.add(
          job_blocks.JobGroup(
              foo=job_blocks.Job(
                  xm_mock.MockExecutable(),
                  xm_mock.MockExecutor(),
                  args={'x': 1, 'y': 2},
                  env_vars={'EDITOR': 'vi'},
              ),
              bar=job_blocks.Job(
                  xm_mock.MockExecutable(),
                  xm_mock.MockExecutor(),
                  args=['--bar=1'],
              ),
          ),
          args={
              'foo': {'args': {'x': 3, 'z': 4}, 'env_vars': {'TURBO': 'ON'}},
              'bar': {'args': ['--spacebar']},
          },
      )

    self.assertEqual(
        experiment.launched_jobs[0].args,
        job_blocks.SequentialArgs.from_collection({'x': 3, 'y': 2, 'z': 4}),
    )
    self.assertEqual(
        experiment.launched_jobs[0].env_vars, {'TURBO': 'ON', 'EDITOR': 'vi'}
    )
    self.assertEqual(
        experiment.launched_jobs[1].args,
        job_blocks.SequentialArgs.from_collection(['--bar=1', '--spacebar']),
    )

  def test_launch_with_different_args(self):
    experiment = xm_mock.MockExperiment()
    with experiment:
      job = job_blocks.Job(xm_mock.MockExecutable(), xm_mock.MockExecutor())
      for i in range(10):
        experiment.add(job, args={'env_vars': {'FOO': i}})

    self.assertEqual(experiment.launched_jobs[0].env_vars, {'FOO': 0})
    self.assertEqual(experiment.launched_jobs[1].env_vars, {'FOO': 1})
    self.assertEqual(experiment.launched_jobs[2].env_vars, {'FOO': 2})

  def test_add_runs_asynchronously(self):
    generator_called = threading.Event()

    with xm_mock.MockExperiment() as experiment:

      async def job_generator(work_unit: core.WorkUnit):
        del work_unit
        generator_called.set()

      experiment.add(job_generator)

      # Validate that job_generator is executed in a parallel thread.
      self.assertTrue(generator_called.wait(timeout=5))

  @utils.run_in_asyncio_loop
  async def test_loop_is_reused_in_coro_context(self):
    loop = asyncio.get_event_loop()

    async with xm_mock.MockExperiment() as experiment:

      async def job_generator(work_unit: core.WorkUnit):
        del work_unit
        self.assertEqual(asyncio.get_event_loop(), loop)

      experiment.add(job_generator)

  @utils.run_in_asyncio_loop
  async def test_sync_with_cant_be_used_in_coro_context(self):
    # `async with` works.
    async with xm_mock.MockExperiment():
      pass

    with self.assertRaises(RuntimeError):
      # But `with` raises an exception.
      with xm_mock.MockExperiment():
        pass

  def test_experiment_works_from_thread_pool(self):
    # There would be no Asyncio even loop thread attahched if running from a
    # worker thread. We ensure that the API still works.
    def launch_experiment():
      experiment = xm_mock.MockExperiment()
      with experiment:
        experiment.add(
            job_blocks.Job(
                xm_mock.MockExecutable(), xm_mock.MockExecutor(), args={}
            )
        )

    with futures.ThreadPoolExecutor() as executor:
      executor.submit(launch_experiment).result()

  @utils.run_in_asyncio_loop
  async def test_work_unit_wait_until_complete(self):
    experiment = xm_mock.MockExperiment()
    async with experiment:
      experiment.add(
          job_blocks.Job(
              xm_mock.MockExecutable(), xm_mock.MockExecutor(), args={}
          )
      )
      completion_future = experiment.work_units[0].wait_until_complete()
      self.assertEqual(completion_future.work_unit.work_unit_id, 1)
      await completion_future

  @utils.run_in_asyncio_loop
  async def test_work_unit_wait_until_complete_exception(self):
    experiment = xm_mock.MockExperiment()
    with self.assertRaises(TestError):
      async with experiment:
        experiment.add(failing_job_generator)
        with self.assertRaises(core.ExperimentUnitError):
          await experiment.work_units[0].wait_until_complete()

  @utils.run_in_asyncio_loop
  async def test_get_full_job_name(self):
    async def generator(work_unit):
      self.assertEqual(work_unit.get_full_job_name('name'), '1_1_name')

    async with xm_mock.MockExperiment() as experiment:
      experiment.add(generator)


class ContextvarsTest(unittest.TestCase):

  def test_contextvars_single_job_launch(self):
    with xm_mock.MockExperiment() as experiment:
      job = job_blocks.Job(xm_mock.MockExecutable(), xm_mock.MockExecutor())
      self.assertEqual(core._current_experiment.get(), experiment)
      experiment.add(job)

    self.assertIsNone(core._current_experiment.get(None))
    self.assertIsNone(core._current_experiment_unit.get(None))

  def test_contextvars_job_group_launch(self):
    with xm_mock.MockExperiment() as experiment:
      foo_job = job_blocks.Job(xm_mock.MockExecutable(), xm_mock.MockExecutor())
      self.assertEqual(core._current_experiment.get(), experiment)
      experiment.add(job_blocks.JobGroup(foo=foo_job))

    self.assertIsNone(core._current_experiment.get(None))
    self.assertIsNone(core._current_experiment_unit.get(None))

  def test_contextvars_job_generator_launch(self):
    with xm_mock.MockExperiment() as experiment:
      self.assertEqual(core._current_experiment.get(), experiment)

      async def job_generator(work_unit: core.WorkUnit):
        self.assertEqual(core._current_experiment_unit.get(), work_unit)
        self.assertEqual(core._current_experiment.get(), work_unit.experiment)

      experiment.add(job_generator)

    self.assertIsNone(core._current_experiment.get(None))
    self.assertIsNone(core._current_experiment_unit.get(None))

  def test_contextvars_async_job_generator_launch(self):
    async def make_experiment():
      async with xm_mock.MockExperiment() as experiment:

        async def job_generator(work_unit: core.WorkUnit):
          self.assertEqual(core._current_experiment_unit.get(), work_unit)
          self.assertEqual(core._current_experiment.get(), work_unit.experiment)

        experiment.add(job_generator)
        self.assertEqual(core._current_experiment.get(), experiment)

      asyncio.run(make_experiment())

    self.assertIsNone(core._current_experiment.get(None))
    self.assertIsNone(core._current_experiment_unit.get(None))

  def test_contextvars_nested_async_job_generator_launch(self):
    async def job_generator(work_unit: core.WorkUnit):
      self.assertEqual(core._current_experiment.get(), work_unit.experiment)
      self.assertEqual(core._current_experiment_unit.get(), work_unit)

    with xm_mock.MockExperiment() as outer_exp:

      async def make_inner_exp():
        async with xm_mock.MockExperiment() as experiment:
          experiment.add(job_generator)
          outer_exp.add(job_generator)
          self.assertEqual(core._current_experiment.get(), experiment)

      asyncio.run(make_inner_exp())
      self.assertEqual(core._current_experiment.get(), outer_exp)

    self.assertIsNone(core._current_experiment.get(None))
    self.assertIsNone(core._current_experiment_unit.get(None))


if __name__ == '__main__':
  unittest.main()
