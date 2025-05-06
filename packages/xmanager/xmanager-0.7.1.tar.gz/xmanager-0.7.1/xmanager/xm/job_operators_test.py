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

import unittest
from unittest import mock
import uuid

from xmanager import xm_mock
from xmanager.xm import job_blocks
from xmanager.xm import job_operators


TEST_UUID = uuid.UUID('40c2fc75-9424-4e33-a929-2e0cc631dccf')


def construct_job(name=None):
  return job_blocks.Job(
      name=name,
      executable=xm_mock.MockExecutable(),
      executor=xm_mock.MockExecutor(),
  )


class JobOperatorsTest(unittest.TestCase):

  def test_collect_jobs_by_filter_gathers_matches(self):
    job_group = job_blocks.JobGroup(
        foo=construct_job('foo'),
        bar=construct_job('bar'),
        baz=construct_job('baz'),
    )

    self.assertEqual(
        job_operators.collect_jobs_by_filter(
            job_group,
            predicate=lambda job: job.name in ['foo', 'baz'],
        ),
        [job_group.jobs['foo'], job_group.jobs['baz']],
    )

  def test_flatten_jobs_traverses_nested_groups(self):
    baz = construct_job('baz')
    foo = construct_job('foo')
    job_group = job_blocks.JobGroup(
        foo=foo,
        bar=job_blocks.JobGroup(baz=baz),
    )

    self.assertEqual(
        job_operators.flatten_jobs(job_group),
        [foo, baz],
    )

  @mock.patch.object(uuid, 'uuid4', return_value=TEST_UUID)
  def test_aggregate_constraint_cliques(self, _):
    outer_1 = construct_job('outer_1')
    inner_1 = construct_job('inner_1')
    inner_2 = construct_job('inner_2')
    constraint_a = xm_mock.MockConstraint('A')
    constraint_b = xm_mock.MockConstraint('B')
    constraint_c = xm_mock.MockConstraint('C')
    job_group = job_blocks.JobGroup(
        outer_1=outer_1,
        outer_2=job_blocks.JobGroup(
            inner_1=inner_1,
            inner_2=inner_2,
            constraints=[constraint_b, constraint_c],
        ),
        constraints=[constraint_a],
    )

    group0_name = f'jobgroup_0_{TEST_UUID.hex}'
    group1_name = f'jobgroup_1_{TEST_UUID.hex}'
    self.assertEqual(
        job_operators.aggregate_constraint_cliques(job_group),
        [
            job_operators.ConstraintClique(
                constraint=constraint_a,
                jobs=[outer_1, inner_1, inner_2],
                group_name=group0_name,
                size=2,
                parent_group_name=None,
            ),
            job_operators.ConstraintClique(
                constraint=constraint_b,
                jobs=[inner_1, inner_2],
                group_name=group1_name,
                size=2,
                parent_group_name=group0_name,
            ),
            job_operators.ConstraintClique(
                constraint=constraint_c,
                jobs=[inner_1, inner_2],
                group_name=group1_name,
                size=2,
                parent_group_name=group0_name,
            ),
        ],
    )


if __name__ == '__main__':
  unittest.main()
