from abc import ABC, abstractmethod
from typing import List, Optional, Any
from dagster import AssetIn, OpExecutionContext, AssetsDefinition
from pydantic import BaseModel

class ModuleBase(BaseModel, ABC):
    """
    A base class for all modules that require parameters.
    This class extends Pydantic's BaseModel to provide validation
    and structured configuration.
    """
    asset_in: Optional[str] = None
    ins_name: str = "data"
    asset_name: str
    group: Optional[str] = None 
    partition: Optional[Any] = None 
    deps: Optional[List[str]] = None
    asset_args:dict = {}
    pk: dict = {}
    

    @abstractmethod
    def create_asset(self) -> AssetsDefinition:
        """
        This is an abstract method that must be implemented by child classes.
        Each module should define how it creates its specific asset.
        """
        pass
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__set_common_asset_args()
        self.display_params()

    def __set_common_asset_args(self) -> None:
        self.asset_args = {
        "group_name": self.group,
        "partitions_def": self.partition.main_partition if self.partition else None,
        "name": self.asset_name,
        "ins": {self.ins_name: AssetIn(self.asset_in)} if self.asset_in else None,
        "deps": self.deps
        }
    def display_params(self) -> None:
        """
        This method can be used to print or display the module's parameters.
        """
        print(f"Asset Name: {self.asset_name}")
        print(f"Asset In: {self.asset_in}")
        print(f"Group: {self.group}")
        print(f"Partition: {self.partition}")
        print(f"Dependencies: {self.deps}")
        #print(f"Required Resources: {self.required_resources}")
        print(f"Asset args: {self.asset_args}")

    def create_pk(self, context:OpExecutionContext) -> None:
        """
        Create partition keys for the read_csv_pandas module
        Pks are used in a string format for injecting partition keys in to the file names, such as dates and static
        Can be used in the configuration as 'data/file/{static}-{date}.csv' for dynamic file fetching/saving
        """
        if not self.partition:
            return
        context.log.info(str(type(self.partition.main_partition)))
        if "Multi" in str(type(self.partition.main_partition)):
            self.pk = context.partition_key.keys_by_dimension
        elif "Daily" in str(type(self.partition.main_partition)):
            self.pk = {"date":context.partition_key}
        else:
            context.log.info("go with static")
            self.pk = {"static":context.partition_key}

    def get_custom_asset_args(self, ins_name):
        """
        Should be used if default ins_name is different than defaults one
        """
        return {
        "group_name": self.group,
        "partitions_def": self.partition.main_partition if self.partition else None,
        "name": self.asset_name,
        "ins": {ins_name: AssetIn(self.asset_in)} if self.asset_in else None,
        "deps": self.deps
        }
    

class TriggerBase(BaseModel, ABC):
    """
    A base class for all modules that require parameters.
    This class extends Pydantic's BaseModel to provide validation
    and structured configuration.
    """
    cur_job:str

    @abstractmethod
    def create_trigger(self):
        """
        This is an abstract method that must be implemented by child classes.
        Each module should define how it creates its specific asset.
        """
        pass


class AssetCheckBase(BaseModel, ABC):
    """
    A base class for all modules that require parameters.
    This class extends Pydantic's BaseModel to provide validation
    and structured configuration.
    """
    asset:str
    @abstractmethod
    def create_check(self):
        """
        This is an abstract method that must be implemented by child classes.
        Each module should define how it creates its specific asset.
        """
        pass