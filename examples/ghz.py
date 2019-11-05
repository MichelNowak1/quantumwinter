from cqc.pythonLib import CQCConnection, qubit
from threading import Thread


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
            measure(Alice, qA)

class ThreadCharlie(Thread):

    def run(self):
        with CQCConnection("Charlie") as Charlie:
            qC = Charlie.recvQubit()
            measure(Charlie, qC)

class ThreadBank(Thread):

    def run(self):
        with CQCConnection("Bob") as Bob:
            qB = Bob.createEPR("Alice")
            qC = qubit(Bob)
            qB.cnot(qC)
            Bob.sendQubit(qC,"Charlie")
            measure(Bob, qB)

ThreadAlice().start()
ThreadCharlie().start()
ThreadBank().start()
