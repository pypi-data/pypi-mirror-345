import numpy as np
from scipy.linalg import qr


def bin2dec(number:str) -> int:
    return sum([int(digit) * 2 ** i for i, digit in enumerate(number[::-1])])


def dec2bin(number:int, digits:int) -> str:
    return bin(number)[2:].zfill(digits)


def get_phase(arraylike_object:np.ndarray) -> float:
    if len(arraylike_object.shape) == 2:
        z = arraylike_object[-1, -1]
    elif len(arraylike_object.shape) == 1:
        z = arraylike_object[-1]
    phi = np.arctan(z.imag / z.real)
    if z.real < 0:
        phi += np.pi
    elif z.real > 0 > z.imag:
        phi += 2 * np.pi
    return phi


# randomly create a NxN-dimensional unitary operator
def random_unitary(num_qubits=1, dtype="float"):
    assert num_qubits >= 1, f"num_qubits should be greater than or equal to 1."
    if dtype == "float":
        N = int(2 ** num_qubits)
        H = np.random.randn(N, N)
        Q, R = qr(H)
    elif dtype == "complex":
        N = int(2 ** num_qubits)
        H_real = np.random.randn(N, N)
        H_imag = np.random.randn(N, N)
        Q, R = qr(H_real + 1j*H_imag)
    else:
        raise AttributeError(f"dtype should be either 'float' or 'complex', not {dtype}")
    return Q


# create a NxN-dimensional unitary operator whose diagonal entries are 1 and the last one is a random phase
def random_phase_unitary(num_qubits=1):
    assert num_qubits >= 1, f"num_qubits should be greater than or equal to 1."
    phi = np.random.randint(0, 359)
    N = int(2 ** num_qubits)
    U = np.eye(N=N, dtype="complex")
    U[-1, -1] = np.exp(1j*phi)
    return U


# randomly create a N-dimensional quantum state
def random_state(num_qubits=1, dtype="float"):
    assert num_qubits >= 1, f"num_qubits should be greater than or equal to 1."
    if dtype == "float":
        angle = 2 * np.pi * np.random.random()
        state = np.array([np.cos(angle), np.sin(angle)])
        if num_qubits == 1:
            return state
        else:
            for _ in range(num_qubits - 1):
                angle = 2 * np.pi * np.random.random()
                state = np.kron(state, np.array([np.cos(angle), np.sin(angle)]))
            return state
    elif dtype == "complex":
        return random_state(num_qubits) + 1j * random_state(num_qubits)
    else:
        raise AttributeError(f"dtype should be either 'float' or 'complex', not {dtype}")


def print_statevector(statevector, decimals=3, ignore_zero_amps=False):
    def for_loop(n, N):
        const = np.round(data[0], decimals)
        sv_str = f"{const} |{bin(0)[2:].zfill(n)}⟩"
        for i in range(1, N):
            const = np.round(data[i], decimals)
            if ignore_zero_amps:
                if abs(const) <= 1e-3:
                    continue
            if const.real < 0:
                sv_str += f" - {-1 * const} |{bin(i)[2:].zfill(n)}⟩"
            else:
                sv_str += f" + {const} |{bin(i)[2:].zfill(n)}⟩"
        return sv_str

    n = len(statevector.dims())
    N = int(2 ** n)
    data = statevector.data
    if N <= 64:
        sv_str = for_loop(n, N)
    else:
        sv_str = for_loop(n, 64)
        const = np.round(data[-1], decimals)
        if const.real < 0:
            sv_str += f" + ... - {-1 * const} |{bin(N - 1)[2:].zfill(n)}⟩"
        else:
            sv_str += f" + ... + {const} |{bin(N - 1)[2:].zfill(n)}⟩"
    print(sv_str)


def order_finder_unitary(x,N):
    k = int(np.ceil(np.log2(N)))
    Ux = np.zeros([2 ** k, 2 ** k], dtype = int)
    for i in range(N):
        Ux[x * i % N][i] = 1
    for i in range(N, 2**k):
        Ux[i][i] = 1
    return Ux


def continuous_fractions(frac, tol=0.0001):
    cf = []
    while True:
        int_part = int(frac)
        float_part = frac - int_part
        if float_part < tol:
            break
        if np.ceil(frac) - frac < tol:
            int_part = round(frac)
        cf.append(int_part)
        frac = float_part ** -1
    return cf


def get_convergents(cont_fracs):
    from fractions import Fraction
    c = []
    convergents = []
    for i in range(len(cont_fracs)):
        c.append(cont_fracs[i])
        for j in range(i - 1, -1, -1):
            c[i] = cont_fracs[j] + 1 / c[i]
        convergents.append(Fraction(c[i]).limit_denominator(10000))
    return convergents


def get_ratios(phase:float):
    cont_fracs = continuous_fractions(phase)
    convergents = get_convergents(cont_fracs)
    ratios = []
    for number in convergents:
        ratios.append({"numerator": number.numerator, "denominator": number.denominator})
    return ratios
