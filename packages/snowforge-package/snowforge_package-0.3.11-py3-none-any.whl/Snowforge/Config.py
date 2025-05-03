import os
import sys
import toml
from .Logging import Debug  # Use existing logging system

class Config:
    """Loads configuration settings from config.toml and manages profiles globally."""

    _config_data = {}
    
    _aws_profile = "default"  # Stores the globally selected profile
    _snowflake_profile = "default"


    CONFIG_FILE_PATHS = [
        os.getenv("SNOWFORGE_CONFIG_PATH"),  # Custom path via env variable
        os.path.join(os.getcwd(), "snowforge_config.toml"),  # Current working directory
        os.path.join(os.path.expanduser("~"), ".config", "snowforge_config.toml"),  # ~/.config/snowforge_config.toml
        os.path.join(os.path.dirname(__file__), "snowforge_config.toml")  # Package directory
    ]

    @staticmethod
    def find_config_file(config_paths: list = CONFIG_FILE_PATHS, verbose: bool = False):
        """Finds the first available config file by searching for the file in locations included in 'config_paths'.
        Args:
            config_paths (list): a list of locations where the script will search for the config. defaults locations are in SNOWFORGE_CONFIG_PATH, Current working dir, '~' and the package dir. You have to create this file yourself in some of these locations and name it 'snowforge_config.toml'.
            verbose (bool): boolean to enable/disable verbose logging. Defaults to 'False'    
        """
        for path in config_paths:
            print(path)
            if path and os.path.exists(path):
                Debug.log(f"found file at: {path}", 'DEBUG', verbose)
                return path
            
        Debug.log("⚠️ No config.toml file found. Exiting..", "WARNING")
        return None
    
    @staticmethod
    def load_config(config_paths: list = CONFIG_FILE_PATHS, verbose: bool = False):
        """Loads the config from the path included in 'config_paths'"""
        config_path = Config.find_config_file(config_paths, verbose)

        # Returns early if no valid path is found
        if not config_path:
            Debug.log(f"No valid file found! Ensure you have created a config file named 'snowforge_config.toml'.", 'ERROR')
            raise FileNotFoundError
        
        try:
            Config._config_data = toml.load(config_path)
            Debug.log(f"Successfully loaded config file from: {config_path}!", 'DEBUG', verbose)
        except toml.TomlDecodeError as e:
            Debug.log(f"Error loading config file\n{e.msg}", 'ERROR')

    @staticmethod
    def get_current_aws_profile()->str:
        return Config._aws_profile

    @staticmethod
    def get_current_snowflake_profile()->str:
        """Returns the current selected snowflake profile."""
        return Config._snowflake_profile
    
    @staticmethod
    def get_snowflake_credentials(config_paths: list = CONFIG_FILE_PATHS, profile: str = "default", verbose: bool = False)->dict:
        """Returns credentials for a given Snowflake profile specified in the snowforge_config.toml file."""
        Config.load_config(config_paths, verbose)
        
        
        sf_config = Config._config_data.get("SNOWFLAKE", {}).get(profile, {})
        if not sf_config:
            Debug.log(f"No profile '{profile}' in .toml file... Please provide a valid configuration.", 'WARNING')
            return None
        
        return sf_config
    
    @staticmethod
    def get_aws_credentials(config_paths: list = CONFIG_FILE_PATHS, profile: str = "default", verbose: bool = False)->dict:
        """Returns credentials for a given AWS profile specified in the snowforge_config.toml file."""
        Config.load_config(config_paths, verbose)

        aws_config = Config._config_data.get("AWS", {}).get(profile, {})

        if not aws_config:
            Debug.log(f"No profile '{profile}' in .toml file... Please provide a valid configuration.", 'WARNING')
            return None
        
        return aws_config