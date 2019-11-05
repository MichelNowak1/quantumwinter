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
            r = randint(0, 1)
            owf_key = bin(BB84_key)[2:] + bin(db_id)[2:] + bin(r)[2:] + bin(M)[2:]
            owf_key = int(abs(hash(owf_key)))%256
            print(owf_key)

            owf_state = qubit(Alice)
            owf_state.rot_X(254)
            #measure(Alice, qA)

class ThreadCharlie(Thread):

    def run(self):
        with CQCConnection("Charlie") as Charlie:
            qC = Charlie.recvQubit()
            #measure(Charlie, qC)

class ThreadBank(Thread):

    def run(self):
        with CQCConnection("Bob") as Bob:
            qB = Bob.createEPR("Alice")
            qC = qubit(Bob)
            qB.cnot(qC)
            Bob.sendQubit(qC,"Charlie")
            #measure(Bob, qB)

ThreadAlice().start()
ThreadCharlie().start()
ThreadBank().start()
