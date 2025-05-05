import os
import yaml
from pydantic import Field, BaseModel
from typing import Optional, Dict
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

### GaiClientConfig

class GaiClientConfig(BaseModel):
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
    def from_dict(cls, config:dict) -> "GaiClientConfig":
        """
        Class method to create an instance of GaiClientConfig from a dictionary.

        Parameters:
            config (dict): A dictionary containing the configuration data.

        Returns:
            GaiClientConfig: An instance of GaiClientConfig populated with the configuration data.

        Usage example:
            config = GaiClientConfig.from_dict(config={
                "url": "https://api.openai.com/v1/engines/davinci-codex/completions",
                "type": "openai",
                "engine": "davinci-codex",
                "model": "davinci-codex",
                "name": "OpenAI Codex",
                "client_type": "openai"
            })
        """        
        return cls._get_client_config(config=config)

    @classmethod
    def _get_gai_config(cls, file_path:str) -> Dict:
        gai_dict = None
        try:
            with open(file_path, 'r') as f:
                gai_dict = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            raise ValueError(f"GaiClientConfig: Error loading client config from file: {e}")
        return gai_dict    

    @classmethod
    def _get_client_config(
            cls,
            name: Optional[str] = None,
            config: Optional[dict] = None,
            file_path: Optional[str] = None    
        ) -> "GaiClientConfig":
        """
        Retrieves a GaiClientConfig object based on the provided arguments.

        Parameters:
            name (str, optional): The name of the configuration.
            config (dict, optional): A dictionary containing the configuration data.
            file_path (str, optional): Path to the configuration file.

        Returns:
            GaiClientConfig: The configuration object based on the provided arguments.

        Raises:
            ValueError: If the arguments are invalid or required keys are missing.

        Usage examples:
            1. Using a dict:
                config = GaiClientConfig.from_dict(config={
                    "url": "https://api.openai.com/v1/engines/davinci-codex/completions",
                    "type": "openai",
                    "engine": "davinci-codex",
                    "model": "davinci-codex",
                    "name": "OpenAI Codex",
                    "client_type": "openai"
                })

            2. Get default ttt config from a specific configuration file:
                config = ClientLLMConfig.from_name(name="ttt", file_path="config.yaml")

            3. Get default ttt config from ~/.gai/gai.yml:
                config = ClientLLMConfig.from_name(name="ttt")
        """
        
        if config:
            return cls(**config)
        
        if name:
            gai_dict = None
            try:
                app_dir=get_app_path()
                global_lib_config_path = os.path.join(app_dir, 'gai.yml')
                if file_path:
                    global_lib_config_path = file_path
                gai_dict = cls._get_gai_config(global_lib_config_path)
            except Exception as e:
                raise ValueError(f"GaiClientConfig: Error loading client config from file: {e}")

            client_config = gai_dict["clients"].get(name, None)
            if not client_config:
                raise ValueError(f"GaiClientConfig: Client Config not found. name={name}")
            return cls(**client_config)
        raise ValueError("GaiClientConfig: Invalid arguments. Either 'name' or 'config' must be provided.")

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

class GaiGeneratorConfig(BaseModel, ABC):
    type: str
    engine: str
    model: str
    name: str
    hyperparameters: Optional[Dict] = {}
    extra: Optional[Dict] = None
    module: ModuleConfig
    class Config:
        extra = "allow"

    @classmethod
    def get_builtin_config(cls):
        pass
    
    @classmethod
    def from_path(cls, path:str):
        pass

    @classmethod
    def from_name(cls,name:str, file_path:str=None) -> "GaiGeneratorConfig":
        return cls._get_generator_config(name=name, file_path=file_path)
    
    @classmethod
    def from_dict(cls, config:dict) -> "GaiGeneratorConfig":
        return cls._get_generator_config(config=config)

    @classmethod
    def _get_gai_config(cls, file_path:str) -> Dict:
        gai_dict = None
        try:
            with open(file_path, 'r') as f:
                gai_dict = yaml.load(f, Loader=yaml.FullLoader)
        except Exception as e:
            raise ValueError(f"GaiGeneratorConfig: Error loading client config from file: {e}")
        return gai_dict    

    @classmethod
    def get_builtin_config_path(cls, this_file) -> str:
        from pathlib import Path
        cfg_file = Path(this_file).resolve().parent / "gai.yml"
        file_path = str(cfg_file)
        return file_path
    
    @classmethod
    def _get_generator_config(
            cls,
            name: Optional[str] = None,
            config: Optional[dict] = None,
            file_path: Optional[str] = None    
        ) -> "GaiGeneratorConfig":
        if config:
            return cls(**config)
        if name:
            gai_dict = None
            try:
                app_dir=get_app_path()
                global_lib_config_path = os.path.join(app_dir, 'gai.yml')
                if file_path:
                    global_lib_config_path = file_path
                gai_dict = cls._get_gai_config(global_lib_config_path)
            except Exception as e:
                raise ValueError(f"GaiClientConfig: Error loading client config from file: {e}")

            if not gai_dict.get("generators"):
                gai_dict["generators"] = {}

            generator_config = gai_dict["generators"].get(name, None)

            if not generator_config:
                
                # Self register the generator config in the gai config
                raise MissingGeneratorConfigError(f"GaiGeneratorConfig: Generator Key {name} is not found in {global_lib_config_path}")
                
                
            # Convert class_ to class before converting to GaiGeneratorConfig
                
            if generator_config["module"].get("class_"):
                generator_config["module"]["class"] = generator_config["module"].pop("class_")
                
            config = cls(**generator_config)
            return config

        raise ValueError("GaiGeneratorConfig: Invalid arguments. Either 'name' or 'config' must be provided.")
    
    def update_gai_config(self, name:str, global_config_path:str=None) -> "GaiConfig":
        
        if not global_config_path:
            app_path = get_app_path()
            global_config_path = os.path.join(app_path, 'gai.yml')
        
        gai_config = GaiConfig.from_path(global_config_path)
        
        if not gai_config.generators:
            gai_config.generators = {}
            
        if gai_config.generators.get(name):
            raise Exception(f"GaiGeneratorConfig: Generator Key {name} already exists in {global_config_path}.")

        gai_config.generators[name]=self.get_builtin_config().model_dump()
        
        with open(global_config_path, "w") as f:
            f.write(gai_config.to_yaml())

        return gai_config    
    


### GaiConfig
    
class GaiConfig(BaseModel):
    version: str
    gai_url: Optional[str] = None
    logging: Optional[LogConfig] = None
    clients: Optional[dict[str,GaiClientConfig] ] = None
    generators: Optional[dict[str,GaiGeneratorConfig] ] = None
    class Config:
        extra = "ignore"
        
    @classmethod
    def from_dict(cls, config):
        return cls(**config)

    @classmethod
    def from_path(cls, file_path=None) -> "GaiConfig":
        """
        Class method to create an instance of GaiConfig from a YAML configuration file.

        Parameters:
            file_path (str, optional): Path to the configuration file. If not provided,
                                       the default path 'gai.yml' in the application directory is used.

        Returns:
            GaiConfig: An instance of GaiConfig populated with the configuration data.

        Usage example:
            config = GaiConfig.from_config()
        """
        app_dir=get_app_path()
        global_lib_config_path = os.path.join(app_dir, 'gai.yml')
        if file_path:
            global_lib_config_path = file_path
        try:
            with open(global_lib_config_path, 'r') as f:
                dict = yaml.load(f, Loader=yaml.FullLoader)
                gai_config = GaiConfig.from_dict(dict)
                return gai_config
            return config
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
        