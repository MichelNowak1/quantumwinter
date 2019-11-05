from cqc.pythonLib import CQCConnection, qubit
from threading import Thread
from random import *
import numpy as np


BB84_key = 2
db_id = 1
pk = 3
sk = 4
M = 400
cheque = []

def one_way_function(conn, BB84_key, db_id, r, M):
    owf_key = bin(BB84_key)[2:] + bin(db_id)[2:] + bin(r)[2:] + bin(M)[2:]
    owf_key = int(abs(hash(str(owf_key))))%256
    owf_state = qubit(conn)
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
            qA = Alice.recvEPR()
            qforC = Alice.recvQubit()
            
            r = randint(0, 1)
            owf_state = one_way_function(Alice, BB84_key, db_id, r, M)

            # Bell state measurement 
            owf_state.cnot(qA)
            owf_state.H()

            qA_measure_result = measure(Alice, qA)
            owf_state_measure_result = measure(Alice, owf_state)

            if qA_measure_result == 0 and owf_state_measure_result == 1:
                qforC.Z()
            if qA_measure_result == 1 and owf_state_measure_result == 0:
                qforC.X()
            if qA_measure_result == 1 and owf_state_measure_result == 1:
                qforC.Y()

            # qforC qubit is now the cheque which is transferred to Charlie
            Alice.sendQubit(qforC, "Charlie")
            cheque.append(db_id)
            cheque.append(r)
            cheque.append(M)


class ThreadCharlie(Thread):

    def run(self):
        with CQCConnection("Charlie") as Charlie:
            qC = Charlie.recvQubit()
            #sendQubit(toto, Bob)
            Charlie.sendQubit(qC, "Bob")

class ThreadBank(Thread):

    def run(self):
        with CQCConnection("Bob") as Bob:
            qB = Bob.createEPR("Alice")
            qA = qubit(Bob)
            qB.cnot(qA)
            Bob.sendQubit(qA,"Alice")
            measure(Bob, qB)

            qC = Bob.recvQubit()
            measure(Bob, qC)

def main():
    ThreadAlice().start()
    ThreadCharlie().start()
    ThreadBank().start()


if __name__ == "__main__":
    # execute only if run as a script
    main()
