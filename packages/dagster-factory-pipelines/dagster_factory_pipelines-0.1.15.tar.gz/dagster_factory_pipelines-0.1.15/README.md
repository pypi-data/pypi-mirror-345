# Dagster Factory Pipelines

This python package allows to create dagster pipelines by using reuseable modules and yaml configuration.

## Features

- Provide base classes for own module, triggers, asset_checks creation and a simple way of registration for new models
- Out of the boxes has predefined modules for http_requests, pandas operations, arcgis, csv store
- Supports templating with jinja syntax
- Configuration of a data pipeline via yaml
- Provides simplify definition for job schedules, triggers, partitions, hooks, i/o manager

### How to use dagster yaml pipelines in the project

```command
pip install dagster-factory-pipelines
```

Define Dagsters defs

```python
from dagster_factory_pipelines import DagsterPipeline

pipeline = DagsterPipeline()
pipeline.run()

defs = pipeline.get_definition()
```

By default DagsterPipelines looking for the `main.yaml` file in the root directory of the python project. It can be changed to any other files if needed.

### How to create own module

Modules can be created in any python files. The most important part to make sure that module is registered during DagsterPipeline runtime.

#### Dagster asset module

There are two requirements for the module. It should use abstract class and it should be registered and accessible to pipeline module during runtime.

ModuleBase abstract class has important information about asset from the yaml configuration, such as asset ins, dependencies, partition, group name, asset name.

```python
@register_module("questdb.api")
class QuestDbGet(ModuleBase):
    """
    Retrieves data from quest db api and store it as a pandas dataframe
    """

    endpoint: str
    query: str
    # auth staff later

    def create_asset(self) -> AssetsDefinition:
        @asset(
            kinds = ["python"],
            description="Gets data from QuestDB and returns as dataframe",
            **self.asset_args
        )
        def get_quest_db_data(context:OpExecutionContext) -> pd.DataFrame:
            self.create_pk(context)
            context.log.info(f"QuestDB endpoint:{self.endpoint}, Query: {self.query}")
            res = Request(self.endpoint, [], None, params={"query":self.query.format(**self.pk)})
            data = res.get_data()
            data = data.json()
            columns = [col["name"] for col in data["columns"]]
            return pd.DataFrame(pd.DataFrame(data.get("dataset"), columns=columns))
        return get_quest_db_data
```

create_asset method should be declared. In this method we simply create traditional dagster asset. We can use all params catched from the yaml file via \*\*self.asset_args argument.

These are required values for the module. For the type checking the base pydantic module is used here.

```python
    endpoint: str
    query: str
```

As a result we can start using this module directly in the configuration file.

```yaml
- asset: quest_db_data
  module: questdb.api
  params:
    endpoint:
    query:
```

If any of required parameters are missing Dagster will notify user about missing values in the configuration.

#### Dagster sensor module

#### Dagster asset check module

## Dagster pipeline

pipeline structured in the logical way for Dagster

```yaml
environment:
  io_manager:
    s3:

resources:
  - resource: name of the registered resource
    name: name of the resource that will be used in dagster
    params: additional params for the defined resource

jobs:
  - template: template_path
    prefix: Optional prefix
    vars:
      var1: var1_value
      ....
      varnN: varN_value

  - job:
      triggers:
        - trigger: registered trigger name
          params:
            param1: param1
            paramN: paramN

      hooks:
        - hook: registered hook name

      partition:
        type: type of the date partition
        start: start date
        end: end date
        elements: list of static elements for the partition

      schedule:
        m: execution minute
        h: hour of execution
        active: state of the schedule
        cron: cron job based schedule required for non partition schedule

      assets:
        - asset: name of the asset
          ins: name of the in(only one possible)
          deps: list of dependencies. Name of the previous assets
          group: name of the group
          module: module name
          params: additional params for module
            param1: param1
            paramN: paramN
          checks: asset checks can be used for non partitioned asset
            - check: name of the registered check
              params:
                param1: param1
                paramN: paramN

        - template: path to asset template
            prefix: prefix for the template
            vars: variables defined in the template
              var1: var1
              varN: varN
```

## Job

At the moment job definition is always required. It is impossible to create asset only pipeline.

Jobs can be defined in two ways. From a separate file via template or directly in the file.

```yaml
jobs:
  - job:

  - template: jobs/template.yaml
```

### Template

Templates support jinja syntax. This allows to create reuseable templates for the repetitive tasks.

templates should start jobs: -job not like job:

Correct syntax for the template

```yaml
jobs:
  - job:

  - template:
```

| **Parameter** | **Type**     | **Required** | **Default Value** | **Description**                                                                                                                                                                                                                                                             |
| ------------- | ------------ | ------------ | ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `prefix`      | String       | No           | None              | Prefix should be used when template is used between many different jobs. Prefix is added to the end of each asset name in a template. The root prefix will overwrite all other defined prefixes if they are present. This flow provides the consistent names for the assets |
| `vars`        | Dict[String] | No           | None              | User can define own variables in a template by using Jinja syntax. It allows to make template reuseable across multiple pipelines.                                                                                                                                          |
| `template`    | String       | Yes          | None              | Path to the template. Relative path to code location.                                                                                                                                                                                                                       |

It is possible define new template in templates.

### Partition

The partition can be defined on a job level. All partitions will be shared across assets inside a job. Many assets provides additional features for partitioned assets.
http module can use stat date and element. It allows dynamically inject partition keys to the API endpoint.

```
partition:
    type: "daily"
    start: "2024-07-20"
    end: "2024-07-21"
    elements:
    - "320669904"
```

| **Parameter** | **Type**     | **Required**                      | **Default Value** | **Description**                                                                                                            |
| ------------- | ------------ | --------------------------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `type`        | String       | required for time based partition | None              | Possible values are `hourly`, `daily`, `weekly`                                                                            |
| `start`       | String       | Yes                               | None              | Format of the date YYYY-mm-dd                                                                                              |
| `end`         | String       | No                                | None              | Should be set if partition will not be using schedules, set time boundary if needed                                        |
| `elements`    | List[String] | No                                | None              | Creates category based partition, can be used together with date partition, in this case a multi partition will be created |

### Triggers

Triggers allow to run a job based on required conditions. To create triggers Dagster Sensor component is used.

Triggers are allowed only on job level. At the moment trigger simply triggers another job, if the previous was successful.

```
  triggers:
    - trigger: on_job
```

| **Parameter** | **Type**     | **Required** | **Default Value** | **Description**                              |
| ------------- | ------------ | ------------ | ----------------- | -------------------------------------------- |
| `trigger`     | String       | Yes          | None              | The name of the registered trigger           |
| `params`      | Dict[String] | No           | None              | Required parameters for the selected trigger |

### Schedule

It is possible to define a schedule for a job. I it is working with both partitioned and non partitioned jobs. In a partition based job the following configuration should be used. For non partition the cron syntax should be used.

| **Parameter** | **Type** | **Required**           | **Default Value** | **Description**                             |
| ------------- | -------- | ---------------------- | ----------------- | ------------------------------------------- |
| `m`           | Integer  | Yes                    | None              | Minute of the execution                     |
| `h`           | Integer  | Yes                    | None              | Hour of the execution                       |
| `active`      | Bool     | No                     | None              | Should schedule be active or not by default |
| `cron`        | String   | Yes(non partition job) | None              | Schedule defined via cronjob syntax         |

Examples:

Partition job

```
schedule:
  m: 00
  h: 3
  active: true
```

At the moment active does not work as it should be.
Ordinary job

```
schedule:
  cron: *****
```

### Hooks

Hooks allows to do a certain action based on the asset execution outcomes.

```
hooks:
  - hook: name of the hook
```

| **Parameter** | **Type** | **Required** | **Default Value** | **Description**             |
| ------------- | -------- | ------------ | ----------------- | --------------------------- |
| `hooks`       | String   | Yes          | None              | Name of the registered hook |

### Assets

All assets defined in the assets block will belong to the job they are defined.

```
assets:
  - asset: name_1
  - template: path_1
```

## Asset

Assets as a Job can be defined in a two ways. Via asset or template. The syntax for the template a bit of different compared to the Jobs template.

```
assets:
  - asset:
```

Asset template has the same variables as a Job template.

| **Parameter** | **Type**     | **Required** | **Default Value** | **Description**                                                                          |
| ------------- | ------------ | ------------ | ----------------- | ---------------------------------------------------------------------------------------- |
| `asset`       | String       | Yes          | None              | Name of the asset                                                                        |
| `ins`         | String       | No           | None              | Name of the asset, which return output the asset should consume                          |
| `deps`        | List[String] | No           | None              | List of the assets on which the current asset depends                                    |
| `group`       | String       | No           | None              | Name of the group where asset should belong                                              |
| `module`      | String       | Yes          | None              | Name of the registered module used for the asset logic                                   |
| `params`      | Dict[String] | No           | None              | parameters that are required by the used module                                          |
| `checks`      | List[Dict]   | No           | None              | Checks that should be used after asset execution. Works for non partitioned assets only. |

## Asset Checks

In some cases it is possible to use asset checks to validate data quality.

| **Parameter** | **Type** | **Required** | **Default Value** | **Description**                         |
| ------------- | -------- | ------------ | ----------------- | --------------------------------------- |
| `check`       | String   | Yes          | None              | Name of the asset check                 |
| `params`      | String   | No           | None              | Required parameters for the asset check |

### When to create a standalone module?

The answer it depends. If its becoming harder to use default modules for example it is hard to achieve desired state
via original modules and several modules are involved in order to make a very simple operation, than it is a good sign that own module is required.
