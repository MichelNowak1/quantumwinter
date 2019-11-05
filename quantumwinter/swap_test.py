from quantum_cheque import one_way_function
from cqc.pythonLib import CQCConnection, qubit
import random
import tqdm

# Initialize the connection
with CQCConnection("Alice") as Alice:
    BB84_key = 2
    db_id = 1
    M = 2
    score = []
    for i in tqdm.tqdm(range(9)):
        salt = random.randint(0, 1000)
        epsilon = random.randint(1,10)
        q = qubit(Alice)
        q11 = qubit(Alice)
        q1 = one_way_function(q11, BB84_key, db_id, salt, M)
        q22 = qubit(Alice)
        q2 = one_way_function(q22, BB84_key, db_id, salt, M)
        q1.cnot(q)
        q2.cnot(q)
        score.append(q.measure())
        # collaspse everything to avoid :
        # cqc.pythonLib.CQCNoQubitError: No more qubits available
        q1.measure()
        q2.measure()

corr = 1. - sum(score)/len(score)

print('average correlation between one_way_function rando; state ==', corr)
 
