from cqc.pythonLib import CQCConnection, qubit
from threading import Thread
from random import *
import numpy as np

BB84_key = 2
db_id = 1
pk = 3
sk = 4
M = 400
cheque = {}

n = 9

def one_way_function(owf_state, BB84_key, db_id, r, M):
    owf_key = bin(BB84_key)[2:] + bin(db_id)[2:] + bin(r)[2:] + bin(M)[2:]
    owf_key = int(abs(hash(str(owf_key))))%256
    owf_state.rot_X(owf_key)
    return owf_state


def measure(conn, q):
    # Measure qubit
    m=q.measure()
    to_print="App {}: Measurement outcome is: {}".format(conn.name,m)
    print("|"+"-"*(len(to_print)+2)+"|")
    print("| "+to_print+" |")
    print("|"+"-"*(len(to_print)+2)+"|")
    return m

class ThreadAlice(Thread):

    def run(self):
        with CQCConnection("Alice") as Alice:
            qA_arr = []
            qforC_arr = []
            for i in range(0, n):
                qA = Alice.recvEPR()
                qA_arr.append(qA)
                qforC = Alice.recvQubit()
                qforC_arr.append(qforC)

            for i in range(0, n):
                r = randint(0, 1)
                owf_state = qubit(Alice)
                owf_state = one_way_function(owf_state, BB84_key, db_id, r, M)

                # Bell state measurement
                owf_state.cnot(qA_arr[i])
                owf_state.H()

                qA_measure_result = measure(Alice, qA_arr[i])
                owf_state_measure_result = measure(Alice, owf_state)

                if qA_measure_result == 0 and owf_state_measure_result == 1:
                    qforC_arr[i].Z()
                if qA_measure_result == 1 and owf_state_measure_result == 0:
                    qforC_arr[i].X()
                if qA_measure_result == 1 and owf_state_measure_result == 1:
                    qforC_arr[i].Y()

            # qforC qubit is now the cheque which is transferred to Charlie
            for i in range(0, n):
                Alice.sendQubit(qforC_arr[i], "Charlie")

            cheque['db_id'] = db_id
            cheque['r'] = r
            cheque['M'] = M


class ThreadCharlie(Thread):

    def run(self):
        with CQCConnection("Charlie") as Charlie:
            qC_arr = []
            for i in range(0, n):
                qC = Charlie.recvQubit()
                qC_arr.append(qC)
                #sendQubit(toto, Bob)

            for i in range(0, n):
                Charlie.sendQubit(qC_arr[i], "Bob")

class ThreadBank(Thread):

    def run(self):
        with CQCConnection("Bob") as Bob:
            qB_arr = []
            for i in range(0, n):
                qB = Bob.createEPR("Alice")
                qB_arr.append(qB)
            print(qB_arr)

            for i in range(0, n):
                qA = qubit(Bob)
                qB.cnot(qA)
                Bob.sendQubit(qA,"Alice")

            # Bob receives cheque
            qC_arr = []
            for i in range(0, n):
                qC = Bob.recvQubit()
                qC_arr.append(qC)

            #for i in range(0, n):
            #    measure(Bob, qC_arr[i])

            for i in range(0, n):
                # Bob performs local computation
                qB_arr[i].H()
                bob_measurement = measure(Bob, qB_arr[i])
                if bob_measurement == 1:
                    qC_arr[i].Z()

            # Bob computes one way function
            owf_bank_state_arr = []
            for i in range(0, n):
                owf_state = qubit(Bob)
                owf_bank_state = one_way_function(owf_state, BB84_key, db_id, cheque['r'], cheque['M'])
                owf_bank_state_arr.append(owf_bank_state)


            score = []
            for i in range(0, n):
                q = qubit(Bob)

                owf_bank_state_arr[i].cnot(q)
                qC_arr[i].cnot(q)

                score.append(q.measure())
                # collaspse everything to avoid :
                # cqc.pythonLib.CQCNoQubitError: No more qubits available
                qC_arr[i].measure()
                owf_bank_state_arr[i].measure()

            corr = 1. - sum(score)/len(score)

            print('average correlation between one_way_function rando; state ==', corr)    


def main():
    ThreadAlice().start()
    ThreadCharlie().start()
    ThreadBank().start()


if __name__ == "__main__":
    # execute only if run as a script
    main()
