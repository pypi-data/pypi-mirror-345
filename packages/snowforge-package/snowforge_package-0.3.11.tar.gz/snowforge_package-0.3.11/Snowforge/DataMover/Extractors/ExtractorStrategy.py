# snowforge/DataMover/Extractors/ExtractorStrategy.py
from abc import ABC, abstractmethod

class ExtractorStrategy(ABC):
    """Abstract base class for all extraction strategies. Think of this like an interface from C#"""

    @abstractmethod
    def extract_table_query(self, fully_qualified_table_name: str, filter_column: str, filter_value: str, verbose: bool = False):
        """Extracts a table based on the provided criteria."""
        pass

    @abstractmethod
    def list_all_tables(self, database_name: str, verbose: bool = False):
        """Lists all tables in a given database."""
        pass
    
    @abstractmethod
    def export_external_table(self, query: str, output_path: str, table_name: str, verbose: bool = False):
        """Exports an external table from a database table."""
        pass