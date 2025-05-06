# Copyright (c) 2025 Munich Quantum Software Company GmbH
# All rights reserved.
#
# This file is part of MQSC PyQDMI. Use of this file is subject to a commercial
# license. See LICENSE.txt for details.

"""MQSC PyQDMI Qiskit Backend."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import numpy as np
from qiskit.circuit import Measure, Parameter
from qiskit.circuit.library import Barrier, CZGate, RGate
from qiskit.providers import BackendV2, Options, QubitProperties
from qiskit.transpiler import InstructionProperties, Target

from mqsc.pyqdmi import Device, Driver, ProgramFormat  # type: ignore[import-not-found]

from .job import QiskitJob

if TYPE_CHECKING:
    from os import PathLike

    from qiskit import QuantumCircuit


__all__ = ["QiskitBackend"]


def __dir__() -> list[str]:
    return __all__


class QiskitBackend(BackendV2):  # type: ignore[misc]
    """MQSC PyQDMI Backend."""

    def __init__(
        self,
        qdmi_device_library: PathLike[str] | str,
        qdmi_prefix: str,
        url: str,
        api_variant: str = "V2",
        token: str | None = None,
        tokens_file: str | None = None,
        auth_server_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize the MQSC PyQDMI Backend.

        Args:
            qdmi_device_library: Path to the QDMI device library.
            qdmi_prefix: Prefix for the QDMI library.
            url: Base URL of the server.
            api_variant: API variant to use.
            token: Token for authentication.
            tokens_file: Path to the file containing tokens.
            auth_server_url: URL of the authentication server.
            username: Username for authentication.
            password: Password for authentication.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)

        self._driver = Driver.get()
        self._driver.load_library(lib_name=str(qdmi_device_library), prefix=qdmi_prefix)
        self._device = self._driver.get_iqm_device(
            base_url=url,
            api_variant=api_variant,
            token=token,
            tokens_file=tokens_file,
            auth_server_url=auth_server_url,
            username=username,
            password=password,
        )
        self._target = self._target_from_device()
        self._max_circuits: int | None = None
        self.name = "MQSC PyQDMI Backend"

    def _target_from_device(self) -> Target:
        """Convert the PyQDMI device to a Qiskit Target.

        Returns:
            The Qiskit Target object.

        Raises:
            ValueError: If the device contains unknown operations.
        """
        num_qubits = self._device.get_qubits_num()
        assert num_qubits > 0, "Number of qubits should be greater than 0"
        sites = self._device.get_sites()
        assert len(sites) > 0, "Sites list should not be empty"
        qubit_properties: list[QubitProperties] = []
        for site in sites:
            site_id = self._device.get_site_id(site)
            assert 0 <= site_id < num_qubits, f"Site ID {site_id} should be between 0 and {num_qubits - 1}"
            site_t1: float | None = None
            try:
                site_t1 = self._device.get_site_t1(site)
                assert site_t1 is not None
                assert site_t1 > 0, f"T1 time for site {site_id} should be greater than 0"
            except RuntimeError:
                pass
            site_t2: float | None = None
            try:
                site_t2 = self._device.get_site_t2(site)
                assert site_t2 is not None
                assert site_t2 > 0, f"T2 time for site {site_id} should be greater than 0"
            except RuntimeError:
                pass
            qubit_properties.append(QubitProperties(t1=site_t1, t2=site_t2))

        target = Target(
            description="PyQDMI Target",
            num_qubits=num_qubits,
            qubit_properties=qubit_properties,
        )

        operations = self._device.get_operations()
        coupling_map = self._device.get_coupling_map()
        assert operations, "Operations dictionary should not be empty"
        for name, operation in operations.items():
            assert name, "Operation name should not be empty"
            assert operation, f"Operation {name} should not be None"

            num_operands = self._device.get_operation_operands_num(operation)
            assert num_operands > 0, f"Operation {name} should have at least one operand"
            num_params = self._device.get_operation_parameters_num(operation)
            assert num_params >= 0, f"Operation {name} should have non-negative number of parameters"

            if num_operands == 1:
                single_qubit_props: dict[tuple[int], InstructionProperties] = {}
                for site in sites:
                    error: float | None = None
                    try:
                        fidelity = self._device.get_operation_fidelity(operation, [site])
                        assert 0 <= fidelity <= 1, f"Fidelity for operation {name} should be between 0 and 1"
                        error = 1.0 - fidelity
                    except RuntimeError:
                        pass
                    duration: float | None = None
                    try:
                        duration = self._device.get_operation_duration(operation, [site])
                        assert duration is not None
                        assert duration >= 0, f"Duration for operation {name} should be greater equal to 0"
                    except RuntimeError:
                        pass
                    site_id = self._device.get_site_id(site)
                    single_qubit_props[site_id,] = InstructionProperties(
                        duration=duration,
                        error=error,
                    )
                if name == "prx":
                    target.add_instruction(
                        instruction=RGate(Parameter("theta"), Parameter("phi")),
                        properties=single_qubit_props,
                    )
                elif name == "measure":
                    target.add_instruction(instruction=Measure(), properties=single_qubit_props)
                else:
                    msg = f"Unknown single qubit operation: {name}"
                    raise ValueError(msg)

            elif num_operands == 2:
                two_qubit_props: dict[tuple[int, ...], InstructionProperties] = {}
                for site1, site2 in coupling_map:
                    error = None
                    try:
                        fidelity = self._device.get_operation_fidelity(operation, [site1, site2])
                        assert 0 <= fidelity <= 1, f"Fidelity for operation {name} should be between 0 and 1"
                        error = 1.0 - fidelity
                    except RuntimeError:
                        pass
                    duration = None
                    try:
                        duration = self._device.get_operation_duration(operation, [site1, site2])
                        assert duration is not None
                        assert duration >= 0, f"Duration for operation {name} should be greater equal to 0"
                    except RuntimeError:
                        pass
                    site1_id = self._device.get_site_id(site1)
                    site2_id = self._device.get_site_id(site2)
                    two_qubit_props[site1_id, site2_id] = InstructionProperties(
                        duration=duration,
                        error=error,
                    )
                if name == "cz":
                    target.add_instruction(instruction=CZGate(), properties=two_qubit_props)
                else:
                    msg = f"Unknown two qubit operation: {name}"
                    raise ValueError(msg)
            else:
                msg = f"Operation {name} has an unsupported number of operands: {num_operands}"
                raise ValueError(msg)
        return target

    @property
    def device(self) -> Device:
        """Get the IQM device."""
        return self._device

    @property
    def target(self) -> Target:
        """Get the target of the backend."""
        return self._target

    @property
    def max_circuits(self) -> int | None:
        """Get the maximum number of circuits that can be run simultaneously."""
        return self._max_circuits

    @max_circuits.setter
    def max_circuits(self, value: int) -> None:
        self._max_circuits = value

    @classmethod
    def _default_options(cls) -> Options:
        return Options()

    def run(self, run_input: QuantumCircuit, **options: dict[str, Any]) -> QiskitJob:
        """Run a quantum circuit on the quantum computer represented by this backend.

        Args:
            run_input: The circuit to run.
            options: Keyword arguments passed to the actual run method.
                     - shots: The number of shots to run the circuit with.
                     - timeout_seconds: The timeout in seconds used to wait for the job to finish.

        Returns:
            Job object from which the results can be obtained once the execution has finished.

        Raises:
            TypeError: If the circuit contains unsupported operations.
        """
        timeout_seconds = options.pop("timeout_seconds", 60.0)
        shots = options.pop("shots", 1024)

        sites = self._device.get_sites()

        instructions = []
        for instruction in run_input.data:
            operation, qargs, cargs = instruction.operation, instruction.qubits, instruction.clbits
            if isinstance(operation, RGate):
                angle_t = float(operation.params[0] / (2 * np.pi))
                phase_t = float(operation.params[1] / (2 * np.pi))
                qubit_loc = run_input.find_bit(qargs[0])
                qubit_index = qubit_loc.registers[0][1]
                instructions.append({
                    "name": "prx",
                    "qubits": [self._device.get_site_name(sites[qubit_index])],
                    "args": {
                        "angle_t": angle_t,
                        "phase_t": phase_t,
                    },
                })
            elif isinstance(operation, Barrier):
                qubit_indices: list[int] = []
                for qubit in qargs:
                    qubit_loc = run_input.find_bit(qubit)
                    qubit_index = qubit_loc.registers[0][1]
                    qubit_indices.append(qubit_index)
                instructions.append({
                    "name": "barrier",
                    "qubits": [self._device.get_site_name(sites[i]) for i in qubit_indices],
                    "args": {},
                })
            elif isinstance(operation, CZGate):
                qubit_loc1 = run_input.find_bit(qargs[0])
                qubit_index1 = qubit_loc1.registers[0][1]
                qubit_loc2 = run_input.find_bit(qargs[1])
                qubit_index2 = qubit_loc2.registers[0][1]
                instructions.append({
                    "name": "cz",
                    "qubits": [
                        self._device.get_site_name(sites[qubit_index1]),
                        self._device.get_site_name(sites[qubit_index2]),
                    ],
                    "args": {},
                })
            elif isinstance(operation, Measure):
                clbit = cargs[0]
                bitloc = run_input.find_bit(clbit)
                creg = bitloc.registers[0][0]
                creg_idx = run_input.cregs.index(creg)
                clbit_index = bitloc.registers[0][1]
                key = f"{creg.name}_{len(creg)}_{creg_idx}_{clbit_index}"
                qubit_loc = run_input.find_bit(qargs[0])
                qubit_index = qubit_loc.registers[0][1]
                instructions.append({
                    "name": "measure",
                    "qubits": [self._device.get_site_name(sites[qubit_index])],
                    "args": {
                        "key": key,
                    },
                })
            else:
                msg = f"Unsupported operation: {operation}"
                raise TypeError(msg)

        program = {
            "name": run_input.name,
            "metadata": {},
            "instructions": instructions,
        }
        program_str = json.dumps(program)

        job = self._device.submit_job(
            program=program_str,
            program_format=ProgramFormat.IQM_JSON,
            num_shots=shots,
            timeout=timeout_seconds,
        )
        return QiskitJob(backend=self, job=job, name=run_input.name)
