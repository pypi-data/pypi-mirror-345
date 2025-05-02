import qandle.operators as op
import abc
import typing
import qandle.utils as utils

__all__ = []


class Ansatz(op.Operator, abc.ABC):
    @abc.abstractmethod
    def decompose(self) -> typing.List[op.Operator]:
        pass


class UnbuiltAnsatz(Ansatz, op.UnbuiltOperator, abc.ABC):
    """An ansatz exposed to the user. Needs to be built before it can be used."""

    @abc.abstractmethod
    def build(self, num_qubits: int, **kwargs) -> "BuiltAnsatz":
        pass


class BuiltAnsatz(Ansatz, op.BuiltOperator, abc.ABC):
    """A built ansatz, ready to be used."""

    def to_matrix(self, **kwargs):
        decomposed = self.decompose()
        decomposed = [
            gate.build(num_qubits=self.num_qubits) if hasattr(gate, "build") else gate
            for gate in decomposed
        ]
        sub_matices = [gate.to_matrix(**kwargs) for gate in decomposed]
        return utils.reduce_dot(*sub_matices)
