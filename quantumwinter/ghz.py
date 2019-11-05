from cqc.pythonLib import CQCConnection, qubit
from threading import Thread
from random import *
import numpy as np


BB84_key = 2
db_id = 1
pk = 3
sk = 4
M = 400

def measure(conn, q):
    # Measure qubit
    m=q.measure()
    to_print="App {}: Measurement outcome is: {}".format(conn.name,m)
    print("|"+"-"*(len(to_print)+2)+"|")
    print("| "+to_print+" |")
    print("|"+"-"*(len(to_print)+2)+"|")


class ThreadAlice(Thread):

    def run(self):
        with CQCConnection("Alice") as Alice:
            qA = Alice.recvEPR()
            qforC = Alice.recvQubit()
            r = randint(0, 1)
            owf_key = bin(BB84_key)[2:] + bin(db_id)[2:] + bin(r)[2:] + bin(M)[2:]
            owf_key = int(abs(hash(str(owf_key))))%256
            owf_state = qubit(Alice)
            owf_state.rot_X(owf_key)
            Alice.sendQubit(qforC, "Charlie")

            # Bell state measurement 
            owf_state.cnot(qA)
            owf_state.H()

            measure(Alice, qA)
            measure(Alice, owf_state)

class ThreadCharlie(Thread):

    def run(self):
        with CQCConnection("Charlie") as Charlie:
            qC = Charlie.recvQubit()
            measure(Charlie, qC)

class ThreadBank(Thread):

    def run(self):
        with CQCConnection("Bob") as Bob:
            qB = Bob.createEPR("Alice")
            qA = qubit(Bob)
            qB.cnot(qA)
            Bob.sendQubit(qA,"Alice")
            measure(Bob, qB)

ThreadAlice().start()
ThreadCharlie().start()
ThreadBank().start()
