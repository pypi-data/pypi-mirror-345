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
"""Utility functions to authenticate with GCP."""

import functools
import os
from typing import Any, Dict, Iterable

from absl import flags
from google import auth
from googleapiclient import discovery
from googleapiclient import errors
from xmanager import xm_flags

_DEFAULT_SCOPES = ('https://www.googleapis.com/auth/cloud-platform',)


def get_project_name() -> str:
  """Gets the Project ID of the GCP Project."""
  _, project = auth.default()
  return project


def get_project_number() -> str:
  """Gets the Project Number of the GCP Project."""
  rm = discovery.build('cloudresourcemanager', 'v1')
  response = rm.projects().get(projectId=get_project_name()).execute()
  return response['projectNumber']


def get_creds(scopes: Iterable[str] = _DEFAULT_SCOPES):
  """Gets the google credentials to be used with GCP APIs."""
  creds, _ = auth.default(scopes=scopes)
  return creds


# The @lru_cache decorator causes this to only be run once per Python session.
@functools.lru_cache()
def enable_apis():
  """Enables APIs on the GCP Project."""
  resource = discovery.build('serviceusage', 'v1')
  body = {
      'serviceIds': [
          'aiplatform.googleapis.com',
          'cloudbuild.googleapis.com',
          'cloudresourcemanager.googleapis.com',
          'compute.googleapis.com',
          'container.googleapis.com',
          'containerregistry.googleapis.com',
          'iam.googleapis.com',
          'logging.googleapis.com',
          'storage-api.googleapis.com',
          'tpu.googleapis.com',
      ]
  }
  resource.services().batchEnable(
      parent=f'projects/{get_project_number()}', body=body
  ).execute()


def get_service_account() -> str:
  """Gets or creates the service account for running XManager in GCP.

  The default Vertex AI Training Service Agent has limited scopes. It is more
  useful to use a custom service account that can access a greater number of
  GCP APIs.

  The `--xm_gcp_service_account_name` flag can be used to specify a user-managed
  service account to be used. If not specified, defaults to `xmanager`.

  Returns:
    The service account email.
  Raises:
    HttpError: if the response was not a 2xx or 403.
  """

  service_account_name = xm_flags.GCP_SERVICE_ACCOUNT_NAME.value
  service_account = (
      f'{service_account_name}@{get_project_name()}.iam.gserviceaccount.com'
  )

  try:
    _maybe_create_service_account(service_account)
    _maybe_grant_service_account_permissions(service_account)
  except errors.HttpError as e:
    # A 403 implies that the user is not an IAM Admin or Cloud Resource Manager
    # API is not enabled.
    # The project admin probably already has set up IAM roles, so the former
    # check can be skipped.
    if e.resp.status != 403 or 'cloudresourcemanager.googleapis.com' in e.uri:
      raise e
  return service_account


def _maybe_create_service_account(service_account: str) -> None:
  """Creates the default service account if it does not exist."""
  iam = discovery.build('iam', 'v1')
  accounts = (
      iam.projects()
      .serviceAccounts()
      .list(name='projects/' + get_project_name())
      .execute()
  )
  for account in accounts.get('accounts', []):
    if account['email'] == service_account:
      return

  # https://cloud.google.com/iam/docs/reference/rest/v1/projects.serviceAccounts
  body = {
      'accountId': service_account.split('@')[0],
      'serviceAccount': {
          'displayName': service_account.split('@')[0],
          'description': 'XManager service account',
      },
  }
  accounts = (
      iam.projects()
      .serviceAccounts()
      .create(name='projects/' + get_project_name(), body=body)
      .execute()
  )


def _maybe_grant_service_account_permissions(service_account: str) -> None:
  """Grants the default service account IAM permissions if necessary."""
  rm = discovery.build('cloudresourcemanager', 'v1')
  policy = rm.projects().getIamPolicy(resource=get_project_name()).execute()
  want_roles = ['roles/aiplatform.user', 'roles/storage.admin']

  should_set = False
  for role in want_roles:
    member = 'serviceAccount:' + service_account
    changed = _add_member_to_iam_policy(policy, role, member)
    should_set = should_set or changed

  if not should_set:
    return None

  body = {'policy': policy}
  rm.projects().setIamPolicy(resource=get_project_name(), body=body).execute()


def _add_member_to_iam_policy(
    policy: Dict[str, Any], role: str, member: str
) -> bool:
  """Modifies the IAM policy to add the member with the role."""
  for i, binding in enumerate(policy['bindings']):
    if binding['role'] == role:
      if member in binding['members']:
        return False
      policy['bindings'][i]['members'].append(member)
      return True

  policy['bindings'].append({'role': role, 'members': [member]})
  return True


def get_bucket() -> str:
  bucket = os.environ.get('GOOGLE_CLOUD_BUCKET_NAME', None)
  if bucket:
    return bucket
  raise ValueError(
      '$GOOGLE_CLOUD_BUCKET_NAME is undefined. Run '
      '`export GOOGLE_CLOUD_BUCKET_NAME=<bucket-name>`, '
      'replacing <bucket-name> with a Google Cloud Storage bucket. '
      'You can create a bucket with '
      '`gsutil mb -l us-central1 gs://$GOOGLE_CLOUD_BUCKET_NAME`'
  )
