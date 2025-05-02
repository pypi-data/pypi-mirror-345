import os
from dagster import Definitions, get_dagster_logger
from pydantic import ValidationError
from . import factory
#from dagster_aws.s3 import S3PickleIOManager, S3Resource
from .models import read_configuration

logger = get_dagster_logger()

class DagsterPipeline:
    def __init__(self):
        self.main_file = "main.yaml"
        
    def run(self):
        self.__read_main_configuration()

    def __read_main_configuration(self):
        try:
            yaml_file = read_configuration(self.main_file)
            factory.Pipeline(**yaml_file)
        # Exception block created by GPT
        except ValidationError as e:
            logger.error("🚨 Validation Errors Detected 🚨")
            for error in e.errors():
                location = " -> ".join(str(loc) for loc in error['loc'])
                print(f"❌ Missing or invalid: '{location}' - {error['msg']}")
               
    def get_definition(self):
        return Definitions(
            assets=factory.ASSET_REPO,
            jobs=factory.JOB_REPO,
            resources=factory.RESOURCE_REPO,
            schedules=factory.SCHEDULES_REPO,
            sensors=factory.TRIGGER_REPO,
            asset_checks=factory.CHECK_REPO
        )
