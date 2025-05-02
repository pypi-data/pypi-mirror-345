from dagster import DagsterRunStatus, DefaultScheduleStatus, DefaultSensorStatus, RunRequest, RunsFilter, sensor
from dagster_factory_pipelines.factory.base import TriggerBase
from dagster_factory_pipelines.factory.registry import register_trigger

@register_trigger("on_job")
class JobDepTrigger(TriggerBase):
    name: str
    job: str
    state: str

    def update_state(self):
        self.state = DefaultSensorStatus.RUNNING if self.state else DefaultScheduleStatus.STOPPED

    def create_trigger(self):
        self.update_state()
        @sensor(name=self.name, job_name=self.cur_job, default_status=self.state)
        def job_completion_sensor(context):

            # Fetch recent run for the dependent job
            runs = context.instance.get_runs(
                filters=RunsFilter(job_name=self.job),
                limit=1,
            )

            # Check if any run exists
            if not runs:
                return

            latest_run = runs[0]
            partition_key = latest_run.tags.get("dagster/partition/date") #TODO it should not be simply data. It was a quick fix for the job trigger

            if not partition_key:
                context.log.warning("No partition key found for the last run.")
                return None
            
            # Use the run ID as a cursor to prevent duplicate triggers
            if context.cursor == latest_run.run_id:
                return

            # Trigger if the run was successful
            if latest_run.status == DagsterRunStatus.SUCCESS:
                context.update_cursor(latest_run.run_id)
                return RunRequest(
                    run_key=f"trigger_{latest_run.run_id}",  # Use unique key per run
                    run_config={},
                    tags={"dagster/partition/date":partition_key} #TODO it should not be simply data. It was a quick fix for the job trigger
                    )
        return job_completion_sensor