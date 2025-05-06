# XManager: A framework for managing machine learning experiments 🧑‍🔬

<!-- Note that links in README.md have to be absolute as it also lands on PyPI. -->

XManager is a platform for packaging, running and keeping track of machine
learning experiments. It currently enables one to launch experiments locally or
on [Google Cloud Platform (GCP)](https://cloud.google.com/). Interaction with
experiments is done via XManager's APIs through Python *launch scripts*. Check
out
[these slides](https://storage.googleapis.com/gresearch/xmanager/deepmind_xmanager_slides.pdf)
for a more detailed introduction.


To get started, install [XManager](#install-xmanager), its
[prerequisites](#prerequisites) if needed and follow [the
tutorial](#writing-xmanager-launch-scripts) or a codelab
([Colab Notebook](https://colab.research.google.com/github/deepmind/xmanager/blob/master/colab_codelab.ipynb) / [Jupyter Notebook](https://github.com/deepmind/xmanager/blob/main/jupyter_codelab.ipynb))
to create and run a launch script.

See
[CONTRIBUTING.md](https://github.com/deepmind/xmanager/blob/main/CONTRIBUTING.md)
for guidance on contributions.

## Install XManager

```bash
pip install git+https://github.com/deepmind/xmanager.git
```

Or, alternatively, [a PyPI project](https://pypi.org/project/xmanager/) is also
available.

```bash
pip install xmanager
```

On Debian-based systems, XManager and all its dependencies can be installed and
set up by cloning this repository and then running

```sh
cd xmanager/setup_scripts && chmod +x setup_all.sh && . ./setup_all.sh
```

## Prerequisites

The codebase assumes Python 3.9+.

### Install Docker (optional)

If you use `xmanager.xm.PythonDocker` to run XManager experiments,
you need to install Docker.

1. Follow [the steps](https://docs.docker.com/engine/install/#supported-platforms)
   to install Docker.

2. And if you are a Linux user, follow [the steps](https://docs.docker.com/engine/install/linux-postinstall/)
   to enable sudoless Docker.

### Install Bazel (optional)

If you use `xmanager.xm_local.BazelContainer` or `xmanager.xm_local.BazelBinary`
to run XManager experiments, you need to install Bazel.

1. Follow [the steps](https://docs.bazel.build/versions/master/install.html) to
   install Bazel.

### Create a GCP project (optional)

If you use `xm_local.Vertex` ([Vertex AI](https://cloud.google.com/vertex-ai))
to run XManager experiments, you need to have a GCP project in order to be able
to access Vertex AI to run jobs.

1. [Create](https://console.cloud.google.com/) a GCP project.

2. [Install](https://cloud.google.com/sdk/docs/install) `gcloud`.

3. Associate your Google Account (Gmail account) with your GCP project by
   running:

   ```bash
   export GCP_PROJECT=<GCP PROJECT ID>
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project $GCP_PROJECT
   ```

4. Set up `gcloud` to work with Docker by running:

   ```bash
   gcloud auth configure-docker
   ```

5. Enable Google Cloud Platform APIs.

   * [Enable](https://console.cloud.google.com/apis/library/iam.googleapis.com)
     IAM.

   * [Enable](https://console.cloud.google.com/apis/library/aiplatform.googleapis.com)
     the 'Cloud AI Platfrom'.

   * [Enable](https://console.cloud.google.com/apis/library/containerregistry.googleapis.com)
     the 'Container Registry'.

6. Create a staging bucket in us-central1 if you do not already have one. This
   bucket should be used to save experiment artifacts like TensorFlow log files,
   which can be read by TensorBoard. This bucket may also be used to stage files
   to build your Docker image if you build your images remotely.

   ```bash
   export GOOGLE_CLOUD_BUCKET_NAME=<GOOGLE_CLOUD_BUCKET_NAME>
   gsutil mb -l us-central1 gs://$GOOGLE_CLOUD_BUCKET_NAME
   ```

   Add `GOOGLE_CLOUD_BUCKET_NAME` to the environment variables or your .bashrc:

   ```bash
   export GOOGLE_CLOUD_BUCKET_NAME=<GOOGLE_CLOUD_BUCKET_NAME>
   ```

## Writing XManager launch scripts

<details>
  <summary>
    A snippet for the impatient 🙂
  </summary>

```python
# Contains core primitives and APIs.
from xmanager import xm
# Implementation of those core concepts for what we call 'the local backend',
# which means all executables are sent for execution from this machine,
# independently of whether they are actually executed on our machine or on GCP.
from xmanager import xm_local
#
# Creates an experiment context and saves its metadata to the database, which we
# can reuse later via `xm_local.list_experiments`, for example. Note that
# `experiment` has tracking properties such as `id`.
with xm_local.create_experiment(experiment_title='cifar10') as experiment:
  # Packaging prepares a given *executable spec* for running with a concrete
  # *executor spec*: depending on the combination, that may involve building
  # steps and / or copying the results somewhere. For example, a
  # `xm.python_container` designed to run on `Kubernetes` will be built via
  #`docker build`, and the new image will be uploaded to the container registry.
  # But for our simple case where we have a prebuilt Linux binary designed to
  # run locally only some validations are performed -- for example, that the
  # file exists.
  #
  # `executable` contains all the necessary information needed to launch the
  # packaged blob via `.add`, see below.
  [executable] = experiment.package([
      xm.binary(
          # What we are going to run.
          path='/home/user/project/a.out',
          # Where we are going to run it.
          executor_spec=xm_local.Local.Spec(),
      )
  ])
  #
  # Let's find out which `batch_size` is best -- presumably our jobs write the
  # results somewhere.
  for batch_size in [64, 1024]:
    # `add` creates a new *experiment unit*, which is usually a collection of
    # semantically united jobs, and sends them for execution. To pass an actual
    # collection one may want to use `JobGroup`s (more about it later in the
    # documentation), but for our purposes we are going to pass just one job.
    experiment.add(xm.Job(
        # The `a.out` we packaged earlier.
        executable=executable,
        # We are using the default settings here, but executors have plenty of
        # arguments available to control execution.
        executor=xm_local.Local(),
        # Time to pass the batch size as a command-line argument!
        args={'batch_size': batch_size},
        # We can also pass environment variables.
        env_vars={'HEAPPROFILE': '/tmp/a_out.hprof'},
    ))
  #
  # The context will wait for locally run things (but not for remote things such
  # as jobs sent to GCP, although they can be explicitly awaited via
  # `wait_for_completion`).
```

</details>

The basic structure of an XManager launch script can be summarized by these
steps:

1. Create an experiment and acquire its context.

    ```python
    from xmanager import xm
    from xmanager import xm_local

    with xm_local.create_experiment(experiment_title='cifar10') as experiment:
    ```

2. Define specifications of executables you want to run.

    ```python
    spec = xm.PythonContainer(
        path='/path/to/python/folder',
        entrypoint=xm.ModuleName('cifar10'),
    )
    ```

3. Package your executables.

    ```python
    [executable] = experiment.package([
      xm.Packageable(
        executable_spec=spec,
        executor_spec=xm_local.Vertex.Spec(),
      ),
    ])
   ```

4. Define your hyperparameters.

    ```python
    import itertools

    batch_sizes = [64, 1024]
    learning_rates = [0.1, 0.001]
    trials = list(
      dict([('batch_size', bs), ('learning_rate', lr)])
      for (bs, lr) in itertools.product(batch_sizes, learning_rates)
    )
    ```

5. Define resource requirements for each job.

    ```python
    requirements = xm.JobRequirements(T4=1)
    ```

6. For each trial, add a job / job groups to launch them.

    ```python
    for hyperparameters in trials:
      experiment.add(xm.Job(
          executable=executable,
          executor=xm_local.Vertex(requirements=requirements),
          args=hyperparameters,
        ))
    ```

Now we should be ready [to run](#run-xmanager) the launch script.

To learn more about different *executables* and *executors* follow
['Components'](#components).

## Run XManager

```bash
xmanager launch ./xmanager/examples/cifar10_tensorflow/launcher.py
```

In order to run multi-job experiments, the `--xm_wrap_late_bindings` flag might
be required:

```bash
xmanager launch ./xmanager/examples/cifar10_tensorflow/launcher.py -- --xm_wrap_late_bindings
```

<!-- TODO: Elaborate on why that is necessary. -->

## Components

### Executable specifications

XManager executable specifications define what should be packaged in the form of
binaries, source files, and other input dependencies required for job execution.
Executable specifications are reusable and generally platform-independent.

See
[executable_specs.md](https://github.com/deepmind/xmanager/blob/main/docs/executable_specs.md)
for details on each executable specification.

| Name | Description |
| --- | --- |
| `xmanager.xm.Container` | A pre-built `.tar` image. |
| `xmanager.xm.BazelContainer` | A [Bazel](https://bazel.build/) target producing a `.tar` image. |
| `xmanager.xm.Binary` | A pre-built binary. |
| `xmanager.xm.BazelBinary` | A [Bazel](https://bazel.build/) target producing a self-contained binary. |
| `xmanager.xm.PythonContainer` | A directory with Python modules to be packaged as a Docker container. |


### Executors

XManager executors define a platform where the job runs and resource
requirements for the job.

Each executor also has a specification which describes how an executable
specification should be prepared and packaged.

See
[executors.md](https://github.com/deepmind/xmanager/blob/main/docs/executors.md)
for details on each executor.

| Name | Description |
| --- | --- |
| `xmanager.xm_local.Local` | Runs a binary or a container locally. |
| `xmanager.xm_local.Vertex` | Runs a container on [Vertex AI](#create-a-gcp-project-(optional)). |
| `xmanager.xm_local.Kubernetes` | Runs a container on Kubernetes. |

### Job / JobGroup

A `Job` represents a single executable on a particular executor, while a
`JobGroup` unites a group of `Job`s providing a gang scheduling concept:
`Job`s inside them are scheduled / descheduled simultaneously. Same `Job`
and `JobGroup` instances can be `add`ed multiple times.

#### Job

A Job accepts an executable and an executor along with hyperparameters which can
either be command-line arguments or environment variables.

Command-line arguments can be passed in list form, `[arg1, arg2, arg3]`:

```bash
binary arg1 arg2 arg3
```

They can also be passed in dictionary form, `{key1: value1, key2: value2}`:

```bash
binary --key1=value1 --key2=value2
```

Environment variables are always passed in `Dict[str, str]` form:

```bash
export KEY=VALUE
```

Jobs are defined like this:

```python
[executable] = xm.Package(...)

executor = xm_local.Vertex(...)

xm.Job(
    executable=executable,
    executor=executor,
    args={
        'batch_size': 64,
    },
    env_vars={
        'NCCL_DEBUG': 'INFO',
    },
)
```

#### JobGroup

A JobGroup accepts jobs in a kwargs form. The keyword can be any valid Python
identifier. For example, you can call your jobs 'agent' and 'observer'.

```python
agent_job = xm.Job(...)
observer_job = xm.Job(...)

xm.JobGroup(agent=agent_job, observer=observer_job)
```
