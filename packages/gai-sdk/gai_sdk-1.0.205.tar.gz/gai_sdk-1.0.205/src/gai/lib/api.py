import os
import sys
import time
import asyncio
import threading
from fastapi import Request

from dotenv import load_dotenv
load_dotenv()

from rich.console import Console
console = Console()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Internal modules
from gai.lib.diagnostics import free_mem
from gai.lib.color import red, green
from gai.lib.config import GaiConfig, GaiGeneratorConfig
from gai.lib.logging import getLogger
logger = getLogger(__name__)

def get_app_version(pyproject_toml):
    import toml
    with open(pyproject_toml) as f:
        pyproject = toml.load(f)
    return pyproject["project"]["version"]

# This tells fastapi which path to host the swagger ui page.
def get_swagger_url():
    swagger_url=None
    if "SWAGGER_URL" in os.environ and os.environ["SWAGGER_URL"]:
        swagger_url=os.environ["SWAGGER_URL"]
        logger.info(f"swagger={swagger_url}")
    else:
        logger.info("swagger_url=disabled.")
    return swagger_url

def configure_cors(app: FastAPI):
    allowed_origins_str = "*"
    if "CORS_ALLOWED" in os.environ:
        allowed_origins_str = os.environ["CORS_ALLOWED"]    # from .env
    allowed_origins = allowed_origins_str.split(",")  # split the string into a list
    logger.info(f"allow_origins={allowed_origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def configure_semaphore():
    use_semaphore = os.getenv("USE_SEMAPHORE", "False").lower() == "true"
    semaphore = None
    if use_semaphore:
        logger.info("Using semaphore")
        import asyncio
        semaphore = asyncio.Semaphore(2)
    return semaphore

async def acquire_semaphore(semaphore):
    while semaphore:
        try:
            await asyncio.wait_for(semaphore.acquire(), timeout=0.1)
            break
        except asyncio.TimeoutError:
            logger.warn("_streaming: Server is busy")
            await asyncio.sleep(1)

def release_semaphore(semaphore):
    if semaphore:
        semaphore.release()
        logger.debug("_streaming: Server is available")

def get_startup_event(
    app,
    category: str,
    pyproject_toml: str,
    generator_config: GaiGeneratorConfig,
):
    async def startup_event():
        
        try:
            # check freemem before loading the model
            free_mem()

            # version check
            logger.info(f"Starting Gai LLM Service ({category}) {get_app_version(pyproject_toml)}")
            
            # extract the default generator config for a category and add it to the app state

            app.state.generator_config = generator_config

            # initialize host and add it to the app state
            host = SingletonHost.GetInstanceFromConfig(generator_config)
            host.load()
            logger.info(f"Model loaded = [{generator_config.name}]")
            app.state.host = host

            # check freemem after loading the model
            free_mem()    
        except Exception as e:
            logger.error(f"Failed to load default model: {e}")
            raise e

    return startup_event

def get_shutdown_event(app):
    
    async def shutdown_event():
        host = app.state.host
        if host:
            host.unload()

    return shutdown_event

def get_generator_config(request: Request) -> GaiGeneratorConfig:
    """
    Dependency to grab the GaiGeneratorConfig you stored in app.state
    """
    return request.app.state.generator_config

def get_generator(request: Request):
    return request.app.state.host.generator

def create_app(pyproject_toml:str, category:str, generator_config: GaiGeneratorConfig):
    
    """
    A helper function to create a FastAPI app with CORS and startup/shutdown events.
    """

    app=FastAPI(
        title="Gai Generators Service",
        description="""Gai Generators Service""",
        version=get_app_version(pyproject_toml),
        docs_url=get_swagger_url()
        )
    configure_cors(app)

    # Event Handlers
    app.add_event_handler("startup", get_startup_event(app, category=category, pyproject_toml=pyproject_toml, generator_config=generator_config))
    app.add_event_handler("shutdown", get_shutdown_event(app))

    return app

class SingletonHost:
    __instance = None       # singleton

    @staticmethod
    def GetInstanceFromPath(generator_name,config_path=None,verbose=True):
        """Static method to access this singleton class's instance."""
        config_path=os.path.expanduser(config_path)
        gai_config = GaiConfig.from_path(config_path)
        gen_config = gai_config.generators[generator_name]
        
        if SingletonHost.__instance == None:
            SingletonHost.__instance=SingletonHost(gen_config,verbose=verbose)
        else:
            # Override __instance's config and verbose if it already exists
            SingletonHost.__instance.config=gen_config
            SingletonHost.__instance.__verbose=verbose
        return SingletonHost.__instance

    @staticmethod
    def GetInstanceFromConfig(config:GaiGeneratorConfig,verbose=True):
        """Static method to access this singleton class's instance."""
        if SingletonHost.__instance == None:
            SingletonHost.__instance=SingletonHost(config,verbose=verbose)
        else:
            # Override __instance's config and verbose if it already exists
            SingletonHost.__instance.config=config
            SingletonHost.__instance.__verbose=verbose
        return SingletonHost.__instance

    def __init__(self,config:GaiGeneratorConfig,verbose=True):
        self.__verbose=verbose

        """Virtually private constructor."""
        if SingletonHost.__instance is not None:
            raise Exception(
                "SingletonHost: This class is a singleton! Access using GetInstance().")
        else:
            # This class only has 4 attributes

            # config is always the first to be loaded from constructor
            self.config = config

            # generator is loaded by calling load()
            self.generator = None

            # generator_name matches config["generator_name"] and is loaded only when self.generator is successfully loaded 
            self.generator_name = None

            # Finally, for thread safety and since this is run locally, use semaphore to ensure only one thread can access the generator at a time
            self.semaphore = threading.Semaphore(1)

            SingletonHost.__instance = self

    def __enter__(self):
        self.load()
        return self
    
    def __exit__(self,exc_type, exc_value,traceback):
        self.unload()
        import gc,torch
        gc.collect()
        torch.cuda.empty_cache()

    # This is idempotent
    def load(self):

        if self.generator_name == self.config.name:
            logger.debug(
                "SingletonHost.load: Generator is already loaded. Skip loading.")
            return self

        if self.generator_name and self.generator_name != self.config.name:
            logger.debug(
                "SingletonHost.load: New generator_name specified, unload current generator.")
            if self.generator:
                self.unload()
                time.sleep(1)

        try:
            target_name=self.config.name
            logger.info(f"SingletonHost: Loading generator {target_name}...")

            # Load generator using reflection
            import importlib
            module = importlib.import_module(self.config.module.name)
            class_ = getattr(module, self.config.module.class_)
            self.generator = class_(generator_config=self.config, verbose=self.__verbose)
            self.generator.load()
            self.generator_name=target_name
            return self
        except Exception as e:
            self.unload()
            logger.error(
                f"SingletonHost: Error loading generator {self.generator_name}: {e}")
            raise e
            
    def unload(self):
        logger.info(f"SingletonHost: Unloading generator {self.generator_name}...")
        if self.generator is not None:

            # Unload the generator which should cause it to unload its components.
            self.generator.unload()

            # Finally delete the generator itself
            del self.generator
            self.generator = None
            self.generator_name = None
            
            # Force garbage collection
            import gc, torch
            gc.collect()
            torch.cuda.empty_cache()            
            
        return self
