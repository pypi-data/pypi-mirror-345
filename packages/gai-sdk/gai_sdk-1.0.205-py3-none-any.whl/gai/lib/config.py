import os
import yaml
from pydantic import Field, BaseModel
from typing import Optional, Dict, Union
from gai.lib.utils import get_app_path
from gai.lib.logging import getLogger
logger = getLogger(__name__)
from abc import ABC, abstractmethod

class LogConfig(BaseModel):
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    datefmt: str = "%Y-%m-%d %H:%M:%S"
    filename: Optional[str] = None
    filemode: str = "a"
    stream: str = "stdout"
    loggers: Optional[Dict] = None

class ConfigBase(BaseModel):
    
    @classmethod
    def _get_gai_config(cls, file_path:str=None) -> Dict:
        
        # if file_path is None, use the default gai config path
        
        if not file_path:
            app_dir=get_app_path()
            file_path = os.path.join(app_dir, 'gai.yml')
        
        try:
            with open(file_path, 'r') as f:
                raw_config = yaml.load(f, Loader=yaml.FullLoader)

            # raw_config is a config that can contain references to other config in the gai config.
            # resolved_config resolves the references to the actual config and replaces them in the config.

            resolved_config = raw_config.copy()
            
            for config_type in ["clients","generators"]:
            
                if config_type in raw_config:
                    
                    # Convert class_ to class before converting to GaiGeneratorConfig
                    
                    for k,v in raw_config[config_type].items():
                        generator_config = v
                        
                        # There are 2 types of configs: generator and alias
                        if v.get("ref",None):
                            ref = v["ref"]
                            generator_config = raw_config[config_type][ref]
                        
                        if generator_config.get("module",None):
                            if generator_config["module"].get("class_",None):
                                generator_config["module"]["class"] = v["module"].pop("class_")
                        
                        resolved_config[config_type][k] = generator_config
                    
        
            return resolved_config
        except Exception as e:
            raise ValueError(f"GaiGeneratorConfig: Error loading client config from file: {e}")
    
### GaiClientConfig

class GaiClientConfig(ConfigBase):
    client_type: str
    type: Optional[str] = None
    engine: Optional[str] = None
    model: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None
    env: Optional[Dict] = None
    extra: Optional[Dict] = None
    hyperparameters: Optional[Dict] = {}

    @classmethod
    def from_name(cls,name:str, file_path:str=None) -> "GaiClientConfig":
        return cls._get_client_config(name=name, file_path=file_path)

    @classmethod
    def from_dict(cls, client_config:dict) -> "GaiClientConfig":
        return cls._get_client_config(client_config=client_config)

    @classmethod
    def _get_client_config(
            cls,
            name: Optional[str] = None,
            client_config: Optional[dict] = None,
            file_path: Optional[str] = None    
        ) -> "GaiClientConfig":
        
        if name:
            
            # If name is provided, load the generator config from gai.yml
            
            try:
                gai_dict = cls._get_gai_config(file_path=file_path)
            except Exception as e:
                raise ValueError(f"GaiClientConfig: Error loading client config from file: {e}")

            client_config = gai_dict["clients"].get(name, None)
            if not client_config:
                raise ValueError(f"GaiClientConfig: Client Config not found. name={name}")
    
        elif client_config:
            pass
        else:
            raise ValueError("GaiClientConfig: Invalid arguments. Either 'name' or 'config' must be provided.")
        
    
        return cls(**client_config)

### GaiGeneratorConfig

class MissingGeneratorConfigError(Exception):
    """Custom Exception with a message"""
    def __init__(self, message):
        super().__init__(message)

class ModuleConfig(BaseModel):
    name: str
    class_: str = Field(alias="class")  # Use 'class' as an alias for 'class_'

    class Config:
        allow_population_by_name = True  # Allow access via both 'class' and 'class_'

class HuggingfaceDownloadConfig(BaseModel):
    type: str
    repo_id: str
    local_dir: str
    revision: str
    file: Optional[str]=None

class DownloadConfig(BaseModel):
    type: str
    local_dir: str

class CivictaiDownloadConfig(DownloadConfig):
    type: str
    url: str
    download: str
    local_dir: str

class GaiAliasConfig(DownloadConfig):
    """
    GaiAliasConfig is a configuration class for aliasing generators with just a reference to the generator name.
    """
    ref: str

class GaiGeneratorConfig(ConfigBase, ABC):
    type: str
    engine: str
    model: str
    name: str
    hyperparameters: Optional[Dict] = {}
    extra: Optional[Dict] = None
    module: ModuleConfig
    source: Optional[DownloadConfig] = None
    class Config:
        extra = "allow"

    @classmethod
    def from_name(cls,name:str, file_path:str=None) -> "GaiGeneratorConfig":
        return cls._get_generator_config(name=name, file_path=file_path)

    @classmethod
    def from_dict(cls, generator_config:dict) -> "GaiGeneratorConfig":
        return cls._get_generator_config(generator_config=generator_config)

    @classmethod
    def get_builtin_config(cls):
        """
        This method should be implemented by the service subclass
        """
        pass
    
    @classmethod
    def from_path(cls, path:str):
        """
        This method should be implemented by the service subclass
        """
        pass

    @classmethod
    def get_builtin_config_path(cls, this_file) -> str:
        """
        This method is for server subclass to locate the server config file
        """
        from pathlib import Path
        cfg_file = Path(this_file).resolve().parent / "gai.yml"
        file_path = str(cfg_file)
        return file_path
    
    @classmethod
    def _get_generator_config(
            cls,
            name: Optional[str] = None,
            generator_config: Optional[dict] = None,
            file_path: Optional[str] = None    
        ) -> "GaiGeneratorConfig":

        if name:
            
            # If name is provided, load the generator config from gai.yml
            
            try:
                gai_dict = cls._get_gai_config(file_path=file_path)
            except Exception as e:
                raise ValueError(f"GaiGeneratorConfig: Error loading generator config from file: {e}")

            generator_config = gai_dict["generators"].get(name, None)
            if not generator_config:
                raise MissingGeneratorConfigError(f"GaiGeneratorConfig: Generator Key {name} is not found in gai.yml")

        elif generator_config:
            pass
        else:
            raise ValueError("GaiGeneratorConfig: Invalid arguments. Either 'name' or 'config' must be provided.")

        # GaiGeneratorConfig Pre-Processing
                
        if generator_config.get("module",None):
            
            # Sometimes "class" maybe stored as class_ after exporting because class is a reserved word in python
            # So we need to convert class_ to class before converting to GaiGeneratorConfig
            
            if generator_config["module"].get("class_",None):
                generator_config["module"]["class"] = generator_config["module"].pop("class_")
            
        return cls(**generator_config)

    
    def update_gai_config(self, global_config_path:str=None) -> "GaiConfig":
        """
        This method is called whenever a generator config is read.
        graft the current generator config into gai config["generators"]
        """
        if not global_config_path:
            app_path = get_app_path()
            global_config_path = os.path.join(app_path, 'gai.yml')
        
        gai_config = GaiConfig.from_path(global_config_path)
        
        if not gai_config.generators:
            gai_config.generators = {}
            
        if gai_config.generators.get(self.name):
            
            # If the generator config already exists in GaiConfig, do not overwrite it
            
            logger.warning(f"GaiGeneratorConfig: Generator Key {self.name} already exists in {global_config_path}.")
            return gai_config

        gai_config.generators[self.name]=self.model_dump()
        
        with open(global_config_path, "w") as f:
            f.write(gai_config.to_yaml())

        return gai_config    

### GaiConfig
    
class GaiConfig(ConfigBase):
    version: str
    gai_url: Optional[str] = None
    logging: Optional[LogConfig] = None
    clients: Optional[dict[str,GaiClientConfig] ] = None
    generators: Optional[dict[str,GaiGeneratorConfig] ] = None
    class Config:
        extra = "ignore"
        
    @classmethod
    def from_dict(cls, config) -> "GaiConfig":
        
        if "generators" in config:
            
            # Convert class_ to class before converting to GaiConfig
            
            for k,v in config["generators"].items():
                if v.get("module",None):
                    if v["module"].get("class_",None):
                        v["module"]["class"] = v["module"].pop("class_")
        
        return cls(**config)

    @classmethod
    def from_path(cls, file_path=None) -> "GaiConfig":
        try:
            gai_dict=cls._get_gai_config(file_path=file_path)
            return GaiConfig.from_dict(gai_dict)        
        except Exception as e:
            raise ValueError(f"GaiConfig: Error loading config from file: {e}")
    
    def to_yaml(self):
        
        # Convert class_ to class before saving
        
        jsoned = self.model_dump()
        if jsoned.get("generators",None):
            for key in jsoned["generators"]:
                if jsoned["generators"][key].get("module",None):
                    if jsoned["generators"][key]["module"].get("class_",None):
                        jsoned["generators"][key]["module"]["class"] = jsoned["generators"][key]["module"].pop("class_")
        
        return yaml.dump(jsoned, sort_keys=False,indent=4)
        