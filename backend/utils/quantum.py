# /Users/1byinf8/Documents/quant-api/utils/quantum.py
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import random

def simulate_bb84(n_bits, eavesdrop=False):
    n_qubits = n_bits * 4
    alice_bits = [random.randint(0, 1) for _ in range(n_qubits)]
    alice_bases = [random.randint(0, 1) for _ in range(n_qubits)]

    circuits = []
    for i in range(n_qubits):
        qc = QuantumCircuit(1, 1)
        if alice_bits[i] == 1:
            qc.x(0)
        if alice_bases[i] == 1:
            qc.h(0)
        circuits.append(qc)

    bob_bases = [random.randint(0, 1) for _ in range(n_qubits)]
    if eavesdrop:
        eve_bases = [random.randint(0, 1) for _ in range(n_qubits)]
        for i in range(n_qubits):
            if eve_bases[i] == 1:
                circuits[i].h(0)
            circuits[i].measure(0, 0)

    for i in range(n_qubits):
        if bob_bases[i] == 1:
            circuits[i].h(0)
        circuits[i].measure(0, 0)

    simulator = AerSimulator()
    bob_bits = []
    for qc in circuits:
        job = simulator.run(qc, shots=1, memory=True)
        result = job.result()
        bob_bits.append(int(result.get_memory()[0]))

    alice_key = [alice_bits[i] for i in range(n_qubits) if alice_bases[i] == bob_bases[i]]
    bob_key = [bob_bits[i] for i in range(n_qubits) if alice_bases[i] == bob_bases[i]]

    if len(alice_key) < n_bits:
        print(f"Warning: Only {len(alice_key)} bits matched, retrying...")
        return simulate_bb84(n_bits, eavesdrop)

    alice_key = alice_key[:n_bits]
    bob_key = bob_key[:n_bits]

    errors = sum(a != b for a, b in zip(alice_key, bob_key))
    error_rate = errors / n_bits if n_bits > 0 else 0

    alice_key_bytes = bytes(int("".join(map(str, alice_key[i:i+8])), 2) for i in range(0, n_bits, 8))
    bob_key_bytes = bytes(int("".join(map(str, bob_key[i:i+8])), 2) for i in range(0, n_bits, 8))

    return alice_key_bytes, bob_key_bytes, error_rate