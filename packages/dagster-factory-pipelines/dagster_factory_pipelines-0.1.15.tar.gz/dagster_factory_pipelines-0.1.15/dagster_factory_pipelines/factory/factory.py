
from datetime import datetime
import os
from typing import List, Literal, Optional, Union
from dagster import RunRequest, schedule, DailyPartitionsDefinition, DefaultScheduleStatus, HourlyPartitionsDefinition, PartitionsDefinition, ScheduleDefinition, StaticPartitionsDefinition, WeeklyPartitionsDefinition, build_schedule_from_partitioned_job, MultiPartitionsDefinition, define_asset_job

from dagster_factory_pipelines.factory.models import read_configuration

from .registry import CHECK_REPO, SCHEDULES_REPO, get_module, get_resource, get_trigger, get_hook, get_check, RESOURCE_REPO, TRIGGER_REPO, ASSET_REPO, JOB_REPO
from pydantic import BaseModel, model_validator
from dagster_aws.s3 import S3PickleIOManager, S3Resource

class Schedule(BaseModel):
    m: Optional[int] = None
    h: Optional[int] = None
    active: Optional[bool] = False
    cron: Optional[str] = None

    m_test:Optional[bool] = False
    # class vars
    job_obj:dict = {}
    job:any = None

    model_config = {"arbitrary_types_allowed":True}
    """
    Crates a schedule based on requirements. For the partition it generates partition based schedule. If there is not partition cron should be specified.
    """
    def create_schedule(self):

        if self.m_test and self.cron:
            # Schedule for a partition that has only static elements, other wise there is no way to trigger schedule for it
            @schedule(cron_schedule=self.cron, job=self.job)
            def continent_schedule():
                for c in self.job_obj["partition"].elements:
                    yield RunRequest(run_key=c, partition_key=c)
            
            SCHEDULES_REPO.append(continent_schedule)           
            return

        if self.job_obj.get("partition"):
            schedule_ = build_schedule_from_partitioned_job(
                self.job,
                hour_of_day=self.h,
                minute_of_hour=self.m,
                default_status= DefaultScheduleStatus.RUNNING if self.active else DefaultScheduleStatus.STOPPED,
            )
        else:
            schedule_ = ScheduleDefinition(
                job_name=self.job_obj.get("name"),
                cron_schedule=self.cron,
                default_status= DefaultScheduleStatus.RUNNING if self.active else DefaultScheduleStatus.STOPPED,
            )
    
        SCHEDULES_REPO.append(schedule_)

class Trigger(BaseModel):
    """
    Creates a simple job trigger sensor. Can be used to trigger another job if the previous one was successful
    """

    trigger: str #name of the trigger in registry
    params: dict #provided params
    cur_job:str = ""


    def create_trigger(self):
        self.params["cur_job"] = self.cur_job
        trigger = get_trigger(self.trigger, self.params)
        TRIGGER_REPO.append(trigger.create_trigger())

class Partition(BaseModel):
    """
    Partition class responsible for creating required partitions based on user configuration.
    It can create date based partitions and also 2D partitions with static data
    """

    type: Optional[Literal["daily", "hourly", "weekly"]] = None # Add enum
    start: Optional[datetime] = None # validate date format YYYY-MM-DD
    end: Optional[datetime] = None
    elements: Optional[List[str]] = None
    # class vars
    date_partition: DailyPartitionsDefinition = None
    elements_partition: StaticPartitionsDefinition = None
    multi_partition: MultiPartitionsDefinition = None
    main_partition: PartitionsDefinition = None

    model_config = {"arbitrary_types_allowed":True}
    def __str__(self):
        return f"type:{self.type}, start:{self.start}"

    def create_date_partition(self):
        if self.type == "daily":
            return DailyPartitionsDefinition(start_date=self.start, end_date=self.end)
        if self.type == "hourly":
            return HourlyPartitionsDefinition(start_date=self.start, end_date=self.end)

        if self.type == "weekly":
            return WeeklyPartitionsDefinition(start_date=self.start, end_date=self.end)
        
    def create_static_partition(self) -> StaticPartitionsDefinition:
        return StaticPartitionsDefinition(self.elements)
    
    def create_partition(self):
        """
        Creates required partition based on user configuration. Safes partition to class vars that can be used in assets.
        """
        if self.elements and self.type:
            self.date_partition = self.create_date_partition()
            self.elements_partition = self.create_static_partition()
            self.multi_partition = MultiPartitionsDefinition(
                {
                    "date": self.date_partition,
                    "static": self.elements_partition,
                }
            )
            self.main_partition = self.multi_partition
            return self
        
        if self.type:
            self.date_partition = self.create_date_partition()
            self.main_partition = self.date_partition
            return self
        
        if self.elements:
            self.elements_partition = self.create_static_partition()
            self.main_partition = self.elements_partition
            return self
        
class Hook(BaseModel):
    hook: str

    def create_hook(self):
        return get_hook(self.hook)


class Resource(BaseModel):
    """
    Resource class allows to create required resources based on user definition
    """

    resource: str
    params: dict
    name: str


    def model_post_init(self, ctx):
        """
        Creates resource automatically and stores in repo
        """
        self.create_resource()


    def create_resource(self):
        """
        Imports resource module, that have been provided by user in the configuration (module: cumo.resources.resources)
        and gets required resource from the module (resource: Cumulocity),
        inits the module with provided paramas in the config (params:)

        Example of config:
        
        module: cumo.resources.resources # imports this module
        resource: Cumulocity # gets this resource
        name: cumulocity
        params: # init module.resource with params
            url: https://tartu.platvorm.iot.telia.ee/measurement/measurements
            username: env(CUMO_USERNAME)
            password: env(CUMO_PASSWORD)

        returns initialized module
        """
        resource = get_resource(self.resource, self.params)
        RESOURCE_REPO[self.name] = resource


class AssetTemplate(BaseModel):

    asset_in: Optional[str] = None

    template: str
    prefix: Optional[str] = None
    vars: Optional[dict] = None
    assets:List = []

    def model_post_init(self, ctx):
        """
        Creates resource automatically and stores in repo
        """
        self.create_assets()

    def apply_prefix(self, asset):
        asset["asset"] += self.prefix
        if "ins" in asset:
            asset["ins"] += self.prefix
        if "deps" in asset:
            asset["deps"] = [dep + self.prefix for dep in asset["deps"]]
        return asset




    def create_assets(self):
        self.vars["env"] = os.environ
        yaml_file = read_configuration(self.template, render_obj=self.vars)
        if yaml_file.get("assets") and self.prefix:
            yaml_file["assets"] = [self.apply_prefix(asset) for asset in yaml_file["assets"]]
        # Refactored by GPT
        # if yaml_file.get("assets") and self.prefix:
        #     for asset in yaml_file.get("assets"):
        #         asset["asset"] += self.prefix
        #         if asset.get("ins"):
        #             asset["ins"] += self.prefix
        #         if asset.get("deps"):
        #             for index, _ in enumerate(asset["deps"]):
        #                 asset["deps"][index] +=  self.prefix

            yaml_file.get("assets")[0]["ins"] = self.asset_in
        print(yaml_file)
        print("pre assetval")
        self.assets = AssetPipeline(**yaml_file).assets

class AssetCheck(BaseModel):
    check: str
    params: Optional[dict] = {}
    asset: str = ""

    def create_asset_check(self):
        check = get_check(self.check, dict(self.params, **{"asset":self.asset}))
        CHECK_REPO.append(check.create_check())

class Asset(BaseModel):
    asset: str
    group: Optional[str] = None
    ins: Optional[List[str]|str] = None
    deps: Optional[List[str]] = None
    module: str
    params: Optional[dict] = {}
    checks: Optional[List[AssetCheck]] = []
    required_params:dict = {}
    """
    Creates assets based on user definition in the config
    """
    # The injection to params is required to give these values directly to the module class
    def inject_asset_name(self) -> None:
        """
        Injects asset_name and asset_in to parameters
        """
        self.required_params["asset_name"] = self.asset
        #if self.module.get("ins"):
        self.required_params["asset_in"] = self.ins

        # inject group
        self.required_params["group"] = self.group

        # inject deps
        self.required_params["deps"] = self.deps


    def create_asset(self) -> None:
        """
        Creates asset based on module and returns asset definition
        """
        self.create_asset_checks()
        self.inject_asset_name()

        module = get_module(self.module, dict(self.params, **self.required_params))
        return module.create_asset()
    

    def create_asset_checks(self) -> None:
        for asset_check in self.checks:
            asset_check.asset = self.asset
            asset_check.create_asset_check()

class Job(BaseModel):
    """
    Creates Jobs based on user config
    """
    job: str # name of the job
    partition: Optional[Partition] = None
    schedule: Optional[Schedule] = None
    assets: List[Union[Asset, AssetTemplate]]
    triggers: Optional[List[Trigger]] = []
    hooks: Optional[List[Hook]] = []

    def model_post_init(self, ctx):
        """
        Creates job automatically and stores in repo
        """
        self.create_job_helper()


    model_config = {"arbitrary_types_allowed":True}

    def create_triggers(self):
        for trigger in self.triggers:
            trigger.cur_job = self.job
            trigger.create_trigger()

    def create_partition(self):
        """
        Creates required partition for the job and stores in partition attribute
        """
        if self.partition:
            self.partition = self.partition.create_partition()

    def create_hooks(self):
        hooks = set()
        for hook in self.hooks:
            hooks.add(hook.create_hook())
        return hooks
    
    def process_asset(self, asset, job_assets):
        if self.partition:
            asset.required_params["partition"] = self.partition
        job_assets.append(asset.create_asset())

    def create_job(self):
        """
        Creates assets for the job and defines a job
        """
        self.create_partition()
        self.create_triggers()
        hooks = self.create_hooks()
        job_assets = []
        for asset in self.assets:
            if isinstance(asset, AssetTemplate):
                for template_asset in asset.assets:
                    self.process_asset(template_asset,job_assets)
            else:
                self.process_asset(asset, job_assets)
        # Refactored by GPT
        # for asset in self.assets:
        #     if isinstance(asset, AssetTemplate):
        #         print(asset)
        #         for template_asset in asset.assets:
        #             print(template_asset)
        #             if self.partition:
        #                 template_asset.required_params["partition"] = self.partition
        #             job_assets.append(template_asset.create_asset())
        #             #ASSET_REPO.extend(job_assets)
        #     else:
        #         if self.partition:
        #             asset.required_params["partition"] = self.partition
        #         job_assets.append(asset.create_asset())
        ASSET_REPO.extend(job_assets)
        
        return define_asset_job(
            self.job,
            selection=job_assets,
            hooks=hooks
            )
    

    def create_job_helper(self):
        job = self.create_job()
        JOB_REPO.append(job)
        # partition based schedule requires job object for the definition
        if self.schedule:
            self.schedule.job_obj = {"partition":self.partition, "name":self.job}
            self.schedule.job = job
            self.schedule.create_schedule()

class S3IoManager(BaseModel):
    endpoint_url: str
    aws_access_key_id: str
    aws_secret_access_key: str
    bucket: str
    def model_post_init(self, ctx):
        self.create_s3_io()

    def create_s3_io(self):
        RESOURCE_REPO["io_manager"] = S3PickleIOManager(
                    s3_resource=S3Resource(
                        endpoint_url="http://"+self.endpoint_url,
                        aws_access_key_id=self.aws_access_key_id,
                        aws_secret_access_key=self.aws_secret_access_key,
                    ),
                    s3_bucket=self.bucket,
                    )

class IoManager(BaseModel):
    s3: S3IoManager

class Environment(BaseModel):
    io_manager: Optional[IoManager] = None


class TemplateJob(BaseModel):
    template: str # location
    vars: Optional[dict]
    prefix: str = ""

    # injecting env os.environ so jinja can get these values if needed
    @model_validator(mode="before")
    def inject_defaults(cls, values):
        # relies on modules_config object
        if not values.get("vars"):
            values["vars"] = {"env":os.environ}
        else:
            values["vars"]["env"] = os.environ
        return values

    def apply_prefix(self, asset):
        if not asset.get("asset"):
            self.replace_child_prefix(asset)
            return asset
        asset["asset"] += self.prefix
        if "ins" in asset:
            asset["ins"] += self.prefix
        if "deps" in asset:
            asset["deps"] = [dep + self.prefix for dep in asset["deps"]]
        return asset
    
    def replace_child_prefix(self, template):
        print("template found")
        template["prefix"] = self.prefix
    def model_post_init(self, ctx):
        """
        Reads new pipeline provided in a template and injects required keys to the jobs assets
        """
        # Refactored by GPT
        # jinja_template = jinja2.Environment().from_string(open(self.template).read())
        # rendered_output = jinja_template.render({"env":os.environ})
        # yaml_file = yaml.safe_load(rendered_output)
        # injecting prefixis this way/ have not found a better way at the moment
        yaml_file = read_configuration(self.template, render_obj=self.vars)
        for job in yaml_file.get("jobs"):
            if job.get("assets"):
                job["assets"] = [self.apply_prefix(asset) for asset in job["assets"]]

            if job.get("template"):
                self.replace_child_prefix(job)
        print(self.prefix)     
        print(yaml_file)
        print("pre job val")
        JobPipeline(**yaml_file)


class JobPipeline(BaseModel):
    jobs: List[Union[Job, TemplateJob]]

class AssetPipeline(BaseModel):
    assets: List[Union[Asset, AssetTemplate]]

class Pipeline(BaseModel):
    environment: Optional[Environment] = None
    resources: Optional[List[Resource]] = None
    jobs: List[Union[Job, TemplateJob]]


