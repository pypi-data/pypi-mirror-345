#! /usr/bin/env python3

"""
szconfig.py is the abstract class for all implementations of SzConfig.
"""

# TODO: Determine specific SzErrors, Errors for "Raises:" documentation.

from abc import ABC, abstractmethod

from .szhelpers import construct_help

# Metadata

__all__ = ["SzConfig"]
__version__ = "0.0.1"  # See https://www.python.org/dev/peps/pep-0396/
__date__ = "2023-10-30"
__updated__ = "2025-01-28"

# -----------------------------------------------------------------------------
# SzConfig
# -----------------------------------------------------------------------------


class SzConfig(ABC):
    """
    SzConfig is the definition of the Senzing Python SDK that is
    implemented by packages such as szconfig.py.
    """

    # -------------------------------------------------------------------------
    # Interface definition
    # -------------------------------------------------------------------------

    @abstractmethod
    def add_data_source(self, data_source_code: str) -> str:
        """
        The `add_data_source` method adds a data source to an existing in-memory configuration.

        Args:
            data_source_code (str): Name of data source code to add.

        Returns:
            str: A string containing a JSON document listing the newly created data source.

        Raises:
            TypeError: Incorrect datatype of input parameter.

        .. collapse:: Example:

            .. literalinclude:: ../../examples/szconfig/add_data_source.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/szconfig/add_data_source.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def delete_data_source(self, data_source_code: str) -> str:
        """
        The `delete_data_source` method removes a data source from an existing in-memory configuration.

        Args:
            data_source_code (str): Name of data source code to delete.

        Raises:
            TypeError: Incorrect datatype of input parameter.

        .. collapse:: Example:

            .. literalinclude:: ../../examples/szconfig/delete_data_source.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/szconfig/delete_data_source.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def export(self) -> str:
        """
        The `export` method creates a JSON string representation of the Senzing SzConfig object.

        Args:

        Returns:
            str: A string containing a JSON Document representation of the Senzing SzConfig object.

        Raises:
            TypeError: Incorrect datatype of input parameter.

        .. collapse:: Example:

            .. literalinclude:: ../../examples/szconfig/export.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/szconfig/export.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def get_data_sources(self) -> str:
        """
        The `get_data_sources` method returns a JSON document of data sources
        contained in an in-memory configuration.

        Args:

        Returns:
            str: A string containing a JSON document listing all of the data sources.

        Raises:
            TypeError: Incorrect datatype of input parameter.

        .. collapse:: Example:

            .. literalinclude:: ../../examples/szconfig/get_data_sources.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/szconfig/get_data_sources.txt
                :linenos:
                :language: json
        """

    # -------------------------------------------------------------------------
    # Convenience methods
    # -------------------------------------------------------------------------

    def help(self, method_name: str = "") -> str:
        """
        Return the help for a particular message.

        Args:
            method_name (str): The name of the method. (e.g. "init"). If empty, a list of methods and descriptions is returned.

        Returns:
            str: The Help information about the requested method
        """
        return construct_help(self, method_name=method_name)
