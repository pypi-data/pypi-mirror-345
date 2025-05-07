from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

class DatabaseIntrospector(ABC):
    """Base class for database introspection."""
    
    @abstractmethod
    def get_table_name(self, model_class) -> str:
        """Get the table name for a model class."""
        pass
    
    @abstractmethod
    def get_columns(self, table_name: str) -> List[Tuple]:
        """Get columns from the database for a given table.
        
        Returns:
            List of tuples containing (column_name, data_type, is_nullable, is_primary, comment)
        """
        pass
    
    @abstractmethod
    def get_indexes(self, table_name: str) -> List[Tuple]:
        """Get indexes from the database for a given table.
        
        Returns:
            List of tuples containing (index_name, index_definition)
        """
        pass
    
    @abstractmethod
    def get_foreign_keys(self, table_name: str) -> List[Tuple]:
        """Get foreign keys from the database for a given table.
        
        Returns:
            List of tuples containing (column_name, foreign_table_name, foreign_column_name)
        """
        pass
    
    def get_schema_for_model(self, model_class, config: Optional[dict] = None) -> Tuple[str, List, List, List]:
        """Get schema information for a model.
        
        This is a default implementation that can be overridden if needed.
        """
        if config is None:
            config = {}
        
        table_name = self.get_table_name(model_class)
        raw_columns = self.get_columns(table_name)
        raw_indexes = self.get_indexes(table_name)
        raw_fks = self.get_foreign_keys(table_name)

        fields = []
        for name, dtype, nullable, is_primary, comment in raw_columns:
            # Skip ignored columns
            if name in config.get("ignore_columns", []):
                continue
                
            type_str = dtype
            if not nullable:
                type_str += " not null"
            if is_primary:
                type_str += ", primary key"
                
            # Handle column comments
            if comment and config.get("with_column_comments", True):
                type_str += f"  # {comment}"
            fields.append((name, type_str))

        indexes = []
        if config.get("show_indexes", True):
            for index_info in raw_indexes:
                if isinstance(index_info, tuple) and len(index_info) >= 2:
                    index_name, definition = index_info[:2]
                    if "UNIQUE" in definition:
                        suffix = "UNIQUE"
                    else:
                        suffix = ""
                    column_match = definition.split("(")[-1].split(")")[0]
                    indexes.append(f"{index_name}  ({column_match}) {suffix}".strip())

        fks = []
        if config.get("show_foreign_keys", True):
            for fk_info in raw_fks:
                if isinstance(fk_info, tuple) and len(fk_info) >= 3:
                    col, ref_table, ref_col = fk_info[:3]
                    fks.append(f"{col} => {ref_table}.{ref_col}")

        return table_name, fields, indexes, fks 