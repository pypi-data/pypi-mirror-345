import importlib.resources as pkg_resources
from .Logging import Debug
from datetime import datetime
from .SnowflakeIntegration import SnowflakeIntegration

class SnowflakeLogging:
    """Handles task logging to snowflake."""

    def __init__():
        pass

    @staticmethod
    def show_requirements(print_to_console=False) -> dict:
        """ Prints the scripts for setting up the required snowflake logging tables, sequences and procedures.
        Returns a dictionary with the SQL files as keys and their content as values.
        The SQL files are located in the resources folder of the package. execute these scripts on your snowflake account to set up the required tables, sequences and procedures.    

        Args:
            print_to_console (bool, optional): If True, prints the SQL to console. Defaults to False.

        Returns:
            dict: A dictionary with the SQL files as keys and their content as values.
        """
        import Snowforge.resources.sql as sql_resources

        sql_files = {}
        for file in pkg_resources.contents(sql_resources):
            print(file)
            if file.endswith(".sql"):
                content = pkg_resources.read_text(sql_resources, file)
                sql_files[file] = content
                if print_to_console:
                    print(f"\n-- {file} --\n{content}")
                    
        return sql_files


    @staticmethod
    def log_start(task_id: int, process_id: int, starttime: datetime, verbose: bool = False) -> int:
        """Logs the start of a task.

        Args:
            task_id (int): The task ID to associate with the log entry.
            process_id (int): The process ID to associate with the log entry.
            starttime (str): The start time of the task.
            verbose (bool, optional): set True to enable DEBUG output. Defaults to False.
        Returns:
            int: The execution ID of the task.
        """
        conn = SnowflakeIntegration.connect(profile="snowforge", verbose=verbose)
        cur = conn.cursor()

        # process id = hash(datetime.now())

        try:
            sql = f"call LOG_TASK_EXECUTION_START({task_id}, {process_id}, TO_TIMESTAMP_LTZ ('{starttime}'));"     
            Debug.log(f"Executing SQL: {sql}", 'DEBUG', verbose)       
            cur.execute(sql)
            conn.commit()
            Debug.log(f"Successfully wrote log start for task '{task_id}'.", 'INFO', verbose)
            return cur.fetchone()[0]
        except Exception as e:
            conn.rollback()
            Debug.log(f"Error writing log start for task '{task_id}' to Snowflake.\n{e}", 'ERROR')
        finally:
            cur.close()

    @staticmethod
    def log_end(execution_id: int, status: str, log_path: str, endtime: datetime, next_execution_time: datetime, verbose: bool = False):
        """Logs the end of a task.

        Args:
            execution_id (int): The execution ID to associate with the log entry.
            status (str): The status of the task.
            log_path (str): The path to the log file.
            endtime (str): The end time of the task.
            next_execution_time (str): The next execution time of the task.
        """
        conn = SnowflakeIntegration.connect(profile="snowforge", verbose=verbose)
        cur = conn.cursor()

        try:
            if next_execution_time is None:
                next_execution_time = 'NULL'
            else:
                next_execution_time = f"TO_TIMESTAMP_LTZ ('{next_execution_time}')"
            
            sql = f"call LOG_TASK_EXECUTION_END({execution_id}, '{status}', '{log_path}',  TO_TIMESTAMP_LTZ ('{endtime}'),  {next_execution_time});"
            Debug.log(f"Executing SQL: {sql}", 'DEBUG', verbose)
            cur.execute(sql)
            conn.commit()
            Debug.log(f"Successfully wrote log end for execution '{execution_id}'.", 'INFO', verbose)
        except Exception as e:
            conn.rollback()
            Debug.log(f"Error writing log end for execution '{execution_id}' to Snowflake.\n{e}", 'ERROR')
        finally:
            cur.close()
            Debug.log("Connection to Snowflake closed.", 'DEBUG', verbose)