from collections.abc import Sequence
import enum


class Driver:
    @staticmethod
    def get() -> Driver:
        """Get the singleton instance"""

    def load_library(self, lib_name: str, prefix: str) -> None:
        """
        Load a QDMI device library into the driver.

        Args:
           lib_name: The name of the library to load. Must be a shared library
                     (e.g. .so, .dll, .dylib). Either given as a full path or just the
                     name of the library. The driver will search for the library in the
                     standard library paths.
           prefix: The prefix of the library, e.g. "IQM" for IQM QDMI device
                   libraries. This prefix is used to load the symbols from the library.
                   The prefix must be the same as the one used when compiling the
                   library.
        """

    def get_iqm_device(self, base_url: str, api_variant: str = 'V2', token: str | None = None, tokens_file: str | None = None, auth_server_url: str | None = None, username: str | None = None, password: str | None = None) -> Device:
        """
        Get a fully configured IQM QDMI device session.

        Args:
           base_url: The base URL of the IQM device.
           api_variant: The API variant to use. Default is "V2".
           token: The access token to use.
           tokens_file: The path to the tokens file.
           auth_server_url: The URL of the authentication server.
           username: The username for authentication.
           password: The password for authentication.

        Returns:
           A QDMI device handle.
        """

class Device:
    def get_qubits_num(self) -> int:
        """Get the number of qubits in the device."""

    def get_sites(self) -> list[Site]:
        """Get the list of sites in the device."""

    def get_operations(self) -> dict[str, Operation]:
        """Get a dictionary that maps names to operations in the device."""

    def get_coupling_map(self) -> list[tuple[Site, Site]]:
        """Get the coupling map of the device."""

    def get_site_id(self, arg: Site, /) -> int:
        """Get the ID of a site."""

    def get_site_t1(self, arg: Site, /) -> float:
        """Get the T1 time of a site."""

    def get_site_t2(self, arg: Site, /) -> float:
        """Get the T2 time of a site."""

    def get_site_name(self, arg: Site, /) -> str:
        """Get the site name."""

    def get_operation_name(self, arg: Operation, /) -> str:
        """Get the name of an operation."""

    def get_operation_operands_num(self, arg: Operation, /) -> int:
        """Get the number of operands for an operation."""

    def get_operation_parameters_num(self, arg: Operation, /) -> int:
        """Get the number of parameters for an operation."""

    def get_operation_fidelity(self, op: Operation, sites: Sequence[Site] | None = None, params: Sequence[float] | None = None) -> float:
        """Get the fidelity of an operation."""

    def get_operation_duration(self, op: Operation, sites: Sequence[Site] | None = None, params: Sequence[float] | None = None) -> float:
        """Get the duration of an operation."""

    def submit_job(self, program: str, program_format: ProgramFormat, num_shots: int, timeout: float = 60.0) -> Job:
        """
        Submit a job to the device.

        Args:
           program: The program to submit.
           program_format: The format of the program.
           num_shots: The number of shots to run.
           timeout: The timeout for the job in seconds. Default is 60 seconds.

        Returns:
           A QDMI job handle.
        """

class Site:
    pass

class Operation:
    pass

class Job:
    def status(self) -> JobStatus:
        """Get the status of a job."""

    def wait(self) -> None:
        """Wait for a job to finish."""

    def cancel(self) -> None:
        """Cancel a job."""

    def get_counts(self) -> dict[str, int]:
        """Get the counts from a job."""

    @property
    def id(self) -> str:
        """Get the job ID."""

    @property
    def num_shots(self) -> int:
        """Get the number of shots for a job."""

class ProgramFormat(enum.Enum):
    _member_names_: list = ...

    _member_map_: dict = ...

    _value2member_map_: dict = ...

    QASM2 = 0

    QASM3 = 1

    QIR_BASE_STRING = 2

    QIR_BASE_MODULE = 3

    QIR_ADAPTIVE_STRING = 4

    QIR_ADAPTIVE_MODULE = 5

    CALIBRATION = 6

    IQM_JSON = 999999995

class JobStatus(enum.Enum):
    _member_names_: list = ...

    _member_map_: dict = ...

    _value2member_map_: dict = ...

    CREATED = 0

    SUBMITTED = 1

    DONE = 2

    RUNNING = 3

    CANCELED = 4
