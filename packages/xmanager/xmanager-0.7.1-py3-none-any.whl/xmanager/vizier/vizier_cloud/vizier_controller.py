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
"""Main code that the Vertex Cloud Vizier Controller runs."""

import time
from typing import Any, Callable, Dict, Optional

from google.cloud import aiplatform_v1beta1 as aip

from xmanager import xm


class VizierController:
  """A Controller that runs Vizier suggested hyperparameters in multiple work units."""

  def __init__(
      self,
      experiment: xm.Experiment,
      work_unit_generator: Callable[[xm.WorkUnit, Dict[str, Any]], Any],
      vz_client: aip.VizierServiceClient,
      study_name: str,
      num_work_units_total: int,
      num_parallel_work_units: int,
  ) -> None:
    """Create a VizierController.

    Args:
      experiment: XM experiment.
      work_unit_generator: the function that generates WorkUnit from
        hyperparameters.
      vz_client: the Vizier Client used for interacting with Vizier.
      study_name: the study name the controller works on.
      num_work_units_total: number of work units to create in total. (TODO:
        remove this and retrieve from study spec stopping criteria once it is
        settable there.)
      num_parallel_work_units: number of work units to run in parallel.
    """
    self._experiment = experiment
    self._work_unit_generator = work_unit_generator
    self._vz_client = vz_client
    self._study_name = study_name
    self._num_work_units_total = num_work_units_total
    self._num_parallel_work_units = num_parallel_work_units

    self._work_unit_updaters = []

  def run(self, poll_frequency_in_sec: float = 60) -> None:
    """Peridically check and sync status between vizier and work units and create new work units when needed."""
    while True:
      # 1. Complete trial for completed work unit; Early stop first if needed.
      for work_unit_updater in self._work_unit_updaters:
        if not work_unit_updater.completed:
          work_unit_updater.check_for_completion()

      # 2. TODO: Return by Vizier's indication that study is done
      # when such API is ready on Vizier side.
      num_exisiting_work_units = len(self._work_unit_updaters)
      num_completed_work_units = sum(
          [wuu.completed for wuu in self._work_unit_updaters]
      )
      if (
          num_exisiting_work_units == self._num_work_units_total
          and num_completed_work_units == self._num_work_units_total
      ):
        print('All done! Exiting VizierController... \n')
        return

      # 3. Get new trials and assign to new work units.
      self._launch_new_work_units()

      time.sleep(poll_frequency_in_sec)

  def _launch_new_work_units(self) -> None:
    """Get hyperparmeter suggestions from Vizier and assign to new work units to run."""
    # 1. Compute num of work units to create next.
    num_existing_work_units = len(self._work_unit_updaters)
    num_running_work_units = len(
        [
            wuu
            for wuu in self._work_unit_updaters
            if wuu.work_unit_status().is_active
        ]
    )
    num_work_units_to_create_total = (
        self._num_work_units_total - num_existing_work_units
    )
    num_work_units_to_create_next = min(
        self._num_parallel_work_units - num_running_work_units,
        num_work_units_to_create_total,
    )

    # 2. Create the work units.
    start_index = num_existing_work_units + 1
    for i in range(start_index, start_index + num_work_units_to_create_next):
      trial = (
          self._vz_client.suggest_trials(
              request=aip.SuggestTrialsRequest(
                  parent=self._study_name,
                  suggestion_count=1,
                  client_id=f'work unit {i}',
              )
          )
          .result()
          .trials[0]
      )
      print(f'Trial for work unit (index: {i}) is retrieved：\n{trial}')

      print(f'Creating work unit (index: {i})... \n')

      def create_gen(index: int, trial: aip.Trial) -> xm.JobGeneratorType:
        async def gen_work_unit(work_unit: xm.WorkUnit, **kwargs):
          await self._work_unit_generator(work_unit, kwargs)

          # TODO: Add an utility to handle logging conditionally
          # (use print when run local otherwise logging.info.)
          print(
              f'Work unit (index: {index}, '
              f'id: {work_unit.work_unit_id}) created. \n'
          )
          self._work_unit_updaters.append(
              WorkUnitVizierUpdater(
                  vz_client=self._vz_client, work_unit=work_unit, trial=trial
              )
          )

        return gen_work_unit

      args = {
          'trial_name': trial.name,
          **{p.parameter_id: p.value for p in trial.parameters},
      }
      self._experiment.add(create_gen(i, trial), args)


class WorkUnitVizierUpdater:
  """An updater for syncing completion state between work unit and vizier trial."""

  def __init__(
      self,
      vz_client: aip.VizierServiceClient,
      work_unit: xm.WorkUnit,
      trial: aip.Trial,
  ) -> None:
    self.completed = False
    self._vz_client = vz_client
    self._work_unit = work_unit
    self._trial = trial

  def work_unit_status(self) -> xm.ExperimentUnitStatus:
    return self._work_unit.get_status()

  def check_for_completion(self) -> None:
    """Sync the completion status between WorkUnit and Vizier Trial if needed."""
    if self.completed:
      return

    print(
        'Start completion check for work unit'
        f' {self._work_unit.work_unit_id}.\n'
    )

    # TODO: Add infeasible_reason when available.
    if not self.work_unit_status().is_active:
      self._complete_trial(self._trial)
      self.completed = True
    elif (
        self._vz_client.check_trial_early_stopping_state(
            request=aip.CheckTrialEarlyStoppingStateRequest(
                trial_name=self._trial.name
            )
        )
        .result()
        .should_stop
    ):
      print(f'Early stopping work unit {self._work_unit.work_unit_id}.\n')
      self._work_unit.stop()
    else:
      print(f'Work unit {self._work_unit.work_unit_id} is still running.\n')

  def _complete_trial(
      self, trial: aip.Trial, infeasible_reason: Optional[str] = None
  ) -> None:
    """Complete a trial."""
    self._vz_client.complete_trial(
        request=aip.CompleteTrialRequest(
            name=trial.name,
            trial_infeasible=infeasible_reason is not None,
            infeasible_reason=infeasible_reason,
        )
    )
    print(f'Trial {trial.name} is completed\n')
