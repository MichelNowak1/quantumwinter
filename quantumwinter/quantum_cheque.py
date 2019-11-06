from cqc.pythonLib import CQCConnection, qubit
from one_way_function import one_way_function
from swap_test import swap_test
from threading import Thread
from random import *
import numpy as np
from swap_test import *

BB84_key = 2
db_id = 1
pk = 3
sk = 4
M = 400
cheque = []

n = 9


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

            # Alice recieves two qubits of every GHZ state from Bank: A1 and A2
            qA_arr = []
            qforC_arr = []
            for i in range(0, n):
                qA = Alice.recvEPR()
                qA_arr.append(qA)

            for i in range(0, n):
                qforC = Alice.recvQubit()
                qforC_arr.append(qforC)

            # Alice uses her supplementary information like:
            # M: amount of money
            # db_id: database ID
            # r: random salting parameter
            # To form a unique key and generates a hashed quantum state
            # from that unique key using the quantum one way function
            for i in range(0, n):
                r = randint(0, 1)
                owf_state = one_way_function(Alice, BB84_key, db_id, r, M)

                # Alice now performs Bell state measurement between
                # her state A1 and the state produced from the quantum one way function
                # To collapse the state and encode the information with the qubit A2
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

                # Here the qubit A2 is ready as the cheque
                cheque_i = {'db_id': db_id, 'r': r, 'M': M}
                cheque.append(cheque_i)

            # A2 qubit (cheque) is transferred to Charlie
            for i in range(0, n):
                Alice.sendQubit(qforC_arr[i], "Charlie")

class ThreadCharlie(Thread):

    def run(self):
        with CQCConnection("Charlie") as Charlie:
            # Charlie receives the cheque from Alice
            qC_arr = []
            for i in range(0, n):
                qC = Charlie.recvQubit()
                qC_arr.append(qC)

            # Charlie sends the cheque to Bank (Bob) to cash it
            for i in range(0, n):
                Charlie.sendQubit(qC_arr[i], "Bob")

class ThreadBank(Thread):

    def run(self):
        with CQCConnection("Bob") as Bob:

            # Bank (Bob) generates the EPR pair and sends
            # two qubits to Alice (A1 and A2)
            qB_arr = []
            for i in range(0, n):
                qB = Bob.createEPR("Alice")
                qB_arr.append(qB)

            for i in range(0, n):
                qA = qubit(Bob)
                qB_arr[i].cnot(qA)
                Bob.sendQubit(qA,"Alice")

            # Bob now waits to receive the cheque from Charlie
            qC_arr = []
            for i in range(0, n):
                qC = Bob.recvQubit()
                qC_arr.append(qC)

            # Bob performs local computation which comprises of
            # Error correction after the bell state measurement performed by Alice
            for i in range(0, n):
                qB_arr[i].H()
                bob_measurement = measure(Bob, qB_arr[i])
                if bob_measurement == 1:
                    qC_arr[i].Z()

            # Bob computes the quantum one way function using the unique key
            # which is obtained from the supplementary information with the cheque
            # like 'r', 'db_id' and 'M'
            # and then performs a SWAP test to see if the result of the quantum one
            # way function is same as the cheque.
            res_same = []
            for i in range(0, n):
                owf_bank_state = one_way_function(Bob,
                    BB84_key, cheque[i]['db_id'], cheque[i]['r'], cheque[i]['M'])

                m_same = swap_test(Bob, owf_bank_state, qC_arr[i])
                res_same.append(m_same)
            print(res_same)


def main():
    ThreadAlice().start()
    ThreadCharlie().start()
    ThreadBank().start()


if __name__ == "__main__":
    # execute only if run as a script
    main()
