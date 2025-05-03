import snowflake.connector as sf
from .Logging import Debug  # Import from same package
from .Config import Config  # Import from same package

class SnowflakeIntegration:
    """Handles establishing and managing connections to Snowflake."""

    DEFAULTS = {
        "snowflake_username": "snowflake username",
        "snowflake_account": "snowflake account"
    }
    
    _connection = None  # Instance variable
    _current_profile = None  # Instance variable


    @staticmethod
    def connect(user_name: str = None, account: str = None, profile: str = "default", verbose: bool = False) -> sf.connection:
        """Establishes a connection to Snowflake.

        Uses either a credentials file or manual login via username and account.

        Args:
            user_name (str, optional): The Snowflake username. Defaults to 'DEFAULTS["snowflake_username"]'.
            account (str, optional): The Snowflake account ID. Defaults to 'DEFAULTS["snowflake_account"]'.
            profile (str, optional): The Snowflake profile to use, must be defined in the 'snowforge_config.toml'. Defaults to 'default'.
            verbose (bool, optional): set True to enable DEBUG output. Defaults to False.

        Returns:
            sf.connection: A Snowflake account connection object.

        Raises:
            sf.errors.Error: If connection fails.
            TypeError: If profile is not found in config file.
            KeyError: If missing key in configuration.
        """

        Debug.log(f"Connecting to Snowflake with profile: '{profile}'", 'DEBUG', verbose)

        if SnowflakeIntegration._connection and not SnowflakeIntegration._connection.is_closed() and SnowflakeIntegration._current_profile == profile:
            Debug.log(f"Reusing existing connection to Snowflake with profile: '{profile}'", 'SUCCESS')
            return SnowflakeIntegration._connection

        if SnowflakeIntegration._connection is not None:
            SnowflakeIntegration._connection.close()
            SnowflakeIntegration._connection = None
            SnowflakeIntegration._current_profile = None

        try:
            # Case 1: If user_name and account are provided → Use external browser
            if user_name and account:
                Debug.log("Using provided username/account with externalbrowser authentication", "DEBUG", verbose)
                SnowflakeIntegration._connection = sf.connect(
                    user=user_name,
                    account=account,
                    authenticator="externalbrowser"
                )

            else:
                # Case 2: Use profile from config
                sf_creds = Config.get_snowflake_credentials(profile=profile)
                config_user_name = sf_creds.get("USERNAME")
                config_account = sf_creds.get("ACCOUNT")
                role = sf_creds.get("ROLE")
                key_file_path = sf_creds.get("KEY_FILE_PATH")
                key_file_password = sf_creds.get("KEY_FILE_PASSWORD")
                database = sf_creds.get("SNOWFLAKE_DATABASE")
                schema = sf_creds.get("SNOWFLAKE_SCHEMA")
                warehouse = sf_creds.get("SNOWFLAKE_WAREHOUSE")

                Debug.log(f"\nSnowflake credentials found for profile '{profile}':\n"
                        f"Username: {config_user_name}\nAccount: {config_account}\nRole: {role}\n"
                        f"Database: {database}\nSchema: {schema}\nWarehouse: {warehouse}\n", 'DEBUG', verbose)

                if key_file_path and key_file_password:
                    SnowflakeIntegration._connection = sf.connect(
                        user=config_user_name,
                        account=config_account,
                        database=database if database else None,
                        schema=schema if schema else None,
                        private_key_file=key_file_path,
                        private_key_file_pwd=key_file_password
                    )

                elif (key_file_password is not None and key_file_path is None) or (key_file_password is None and key_file_path is not None):
                    Debug.log("Key file path and password must be provided together. Please check you .toml file", 'ERROR')
                    raise sf.errors.ConfigSourceError

                else:
                    SnowflakeIntegration._connection = sf.connect(
                        user=config_user_name,
                        account=config_account,
                        authenticator="externalbrowser"
                    )

            SnowflakeIntegration._current_profile = profile
            Debug.log(f"Successfully connected to Snowflake with profile: '{profile}'!", 'SUCCESS')
            Debug.log("Connection details:\n" +
                    f"{'Username:':<15} {SnowflakeIntegration._connection.user}\n" +
                    f"{'Account:':<15} {SnowflakeIntegration._connection.account}\n" +
                    f"{'Role:':<15} {SnowflakeIntegration._connection.role}\n" +
                    f"{'Database:':<15} {SnowflakeIntegration._connection.database}\n" +
                    f"{'Schema:':<15} {SnowflakeIntegration._connection.schema}\n" +
                    f"{'Warehouse:':<15} {SnowflakeIntegration._connection.warehouse}",
                    'SUCCESS', verbose)

            return SnowflakeIntegration._connection

        except Exception as e:
            Debug.log(f"Could not connect to Snowflake. Error: {e}", 'ERROR')
            raise sf.errors.ConfigSourceError
    
    @staticmethod
    def truncate_table(database: str, schema: str, table: str, profile: str = "default", verbose: bool = False):
        """Truncates a table in Snowflake.

        Args:
            database (str): The Snowflake database containing the table to truncate.
            schema (str): The Snowflake schema containing the table to truncate.
            table (str): The Snowflake table to truncate.
            profile (str, optional): The Snowflake profile to use, must be defined in the 'snowforge_config.toml'. Defaults to 'default'.
            verbose (bool, optional): set True to enable DEBUG output. Defaults to False.

        Raises:
            sf.errors.ProgrammingError: If the table does not exist or if the connection fails.
        """
        if SnowflakeIntegration._connection is None or SnowflakeIntegration._connection.is_closed():
            connection = SnowflakeIntegration.connect(profile=profile, verbose=verbose)
            SnowflakeIntegration._connection = connection

        cur = SnowflakeIntegration._connection.cursor()

        try:
            cur.execute(f"TRUNCATE TABLE {database}.{schema}.{table}")
            Debug.log(f"Successfully truncated table '{table}'.", 'SUCCESS', verbose)

        except sf.errors.ProgrammingError as e:
            Debug.log(f"Error truncating table '{table}'.\n{e}", 'ERROR')
        finally:
            cur.close()

    @staticmethod
    def load_to_snowflake(stage: str, stage_key: str, database: str = None, schema: str = None, table: str = None, profile: str = "default", verbose: bool = False):
        """Loads a file to Snowflake.

        Args:
            stage (str): The Snowflake stage to load the file from.
            stage_key (str): The key of the file to load.
            database (str, optional): The Snowflake database to load the file into. Defaults to None.
            schema (str, optional): The Snowflake schema to load the file into. Defaults to None.
            table (str, optional): The Snowflake table to load the file into. Defaults to None.
            profile (str, optional): The Snowflake profile to use, must be defined in the 'snowforge_config.toml'. Defaults to 'default' if no connection is already established.
            verbose (bool, optional): set True to enable DEBUG output. Defaults

        Raises:
            sf.errors.ProgrammingError: If file_path is invalid.
        """
        if SnowflakeIntegration._connection is None or SnowflakeIntegration._connection.is_closed():
            connection = SnowflakeIntegration.connect(profile=profile, verbose=verbose)
            SnowflakeIntegration._connection = connection

        cur = SnowflakeIntegration._connection.cursor()

        try:
            cur.execute(f"COPY INTO {database}.{schema}.{table} FROM @{stage}{stage_key} FILE_FORMAT=(TYPE=CSV FIELD_DELIMITER ='|' ESCAPE = '\\\\' FIELD_OPTIONALLY_ENCLOSED_BY='\"' NULL_IF = ('NULL', ''))")

            Debug.log(f"Successfully loaded file '{stage_key}' to Snowflake table '{table}'.", 'SUCCESS', verbose)

        except sf.errors.ProgrammingError as e:
            Debug.log(f"Error loading file '{stage_key}' to Snowflake table '{table}'.\n{e}", 'ERROR')
        finally:
            cur.close()

    @staticmethod
    def close_connection():
        """Closes the Snowflake connection if it is open."""
        if SnowflakeIntegration._connection and not SnowflakeIntegration._connection.is_closed():
            SnowflakeIntegration._connection.close()
            Debug.log("Snowflake connection closed.", 'DEBUG')
        else:
            Debug.log("No active Snowflake connection to close.", 'DEBUG')