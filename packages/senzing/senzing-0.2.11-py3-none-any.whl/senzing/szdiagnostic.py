#! /usr/bin/env python3

"""
szdiagnostic.py is the abstract class for all implementations of SzDiagnostic.
"""

from abc import ABC, abstractmethod

from .szhelpers import construct_help

# Metadata

__all__ = ["SzDiagnostic"]
__version__ = "0.0.1"  # See https://www.python.org/dev/peps/pep-0396/
__date__ = "2023-10-30"
__updated__ = "2025-01-28"

# -----------------------------------------------------------------------------
# SzDiagnostic
# -----------------------------------------------------------------------------


class SzDiagnostic(ABC):
    """
    Senzing diagnostic module access library
    """

    # -------------------------------------------------------------------------
    # Interface definition
    # -------------------------------------------------------------------------

    @abstractmethod
    def check_datastore_performance(self, seconds_to_run: int) -> str:
        """
        The `check_datastore_performance` method performs inserts to determine rate of insertion.

        Args:
            seconds_to_run (int): Duration of the test in seconds.

        Returns:
            str: A string containing a JSON document.

        Raises:
            TypeError: Incorrect datatype of input parameter.
            szexception.SzError:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/szdiagnostic/check_datastore_performance.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/szdiagnostic/check_datastore_performance.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def get_datastore_info(self) -> str:
        """
        The `get_datastore_info` method returns a JSON document with details of the datastore
        currently in use by Senzing.

        Raises:
            szexception.SzError:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/szdiagnostic/get_datastore_info.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/szdiagnostic/get_datastore_info.txt
                :linenos:
                :language: json
        """

    # NOTE This is experimental and for internal diagnostics, not to be documented
    @abstractmethod
    def get_feature(self, feature_id: int) -> str:  # pylint: disable=empty-docstring
        """"""

    @abstractmethod
    def purge_repository(self) -> None:
        """
        **Warning:**
        The `purge_repository` method removes every record in the Senzing repository.

        Before calling `purge_repository` all other instances of the Senzing API
        MUST be destroyed or shutdown.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/szdiagnostic/purge_repository.py
                :linenos:
                :language: python
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
