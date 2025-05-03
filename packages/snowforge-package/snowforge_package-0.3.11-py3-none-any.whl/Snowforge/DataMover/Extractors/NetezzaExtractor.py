import subprocess
import os
from .ExtractorStrategy import ExtractorStrategy
from ...Logging import Debug

class NetezzaExtractor(ExtractorStrategy):
    """Handles extraction from Netezza specifically."""

    def extract_table_query(self, fully_qualified_table_name: str, filter_column: str = None, filter_value: str = None, verbose: bool = False)->str:
        """Build query against database table. (Can be extended in a future version)."""
        
        if filter_column is not None and filter_value is None:
            Debug.log(f"You must provide a filter value in order to apply any filtering.", 'WARNING')
            raise Exception
        
        elif filter_column is None and filter_value is not None:
            Debug.log(f"You cannot supply a filter value without specifying a filter (--filter option)\ncontinuing without filter.", 'WARNING')
            raise Exception
        
        if filter_value is None or filter_column is None:
            query = f"SELECT * FROM {fully_qualified_table_name}"
        else:
            query = f"SELECT * FROM {fully_qualified_table_name} WHERE {filter_column} BETWEEN TO_DATE('{filter_value}', 'DD.MM.YYYY') AND CURRENT_DATE+1"
        
        return query

    def list_all_tables(self, database_name: str, verbose: bool = False)->list:
        """Query all tables in the specified database and export them as an array."""
        
        command = f"nzsql -q -c \"SELECT TABLE_NAME FROM _V_TABLE WHERE TABLE_SCHEMA = '{database_name}';\""
        output = subprocess.check_output(command, shell=True).decode('ISO-8859-1')
        table_list = [line.strip() for line in output.split('\n') if line.strip()]

        return table_list

    def export_external_table(self, output_path: str, fully_qualified_table_name: str, filter_column: str = None, filter_value: str = None, verbose: bool = False)->tuple:
        """Runs the query on Netezza and exports the data to a CSV file.
        Requires NZ_HOME, NZ_USER, NZ_PASSWORD and NZ_DATABASE environment variables to be set."""
        
        table_name = fully_qualified_table_name.split('.')[-1] if fully_qualified_table_name else None

        query = self.extract_table_query(fully_qualified_table_name, filter_column, filter_value, verbose)

        os.makedirs(output_path, exist_ok=True)
        exported_csv_file = os.path.join(output_path, f"{table_name}_full.csv")

        with open(exported_csv_file, 'w') as f:
            pass
        
                                    
        external_table_query = f"""
        CREATE EXTERNAL TABLE '{exported_csv_file}' 
        USING (
            REMOTESOURCE 'NZSQL'
            delimiter '|'
            escapeChar '\\'
            QuotedValue 'Double'
            nullValue 'NULL'
            encoding 'internal'
        )
        AS {query};
        """
        encoding_command = f"iconv -f ISO-8859-1 -t UTF-8 {exported_csv_file} -o {exported_csv_file}"
        nzsql_command = f"""$NZ_HOME/nzsql -c "{external_table_query}" """

        try:
            Debug.log(f"Running command: {encoding_command}", 'DEBUG', verbose)
            subprocess.run(encoding_command, shell=True, check=True)

            subprocess.run(nzsql_command, shell=True, check=True)
            
        except subprocess.CalledProcessError as e:
            Debug.log(f"Error executing Netezza command: {e}", 'ERROR')
            return None, None
        
        header = "ddd"
        return header, exported_csv_file
    