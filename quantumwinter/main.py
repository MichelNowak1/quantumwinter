from cqc.pythonLib import CQCConnection, qubit
from threading import Thread
from random import *
import numpy as np
from A_party import A_party
from B_party import B_party


len_BB84_key = 8

class ThreadAlice(Thread):

    def run(self):
        with CQCConnection("Alice") as Alice:
            BB84_key = A_party(len_BB84_key)       

class ThreadBank(Thread):

    def run(self):
        with CQCConnection("Bob") as Bob:
            BB84_key = B_party(len_BB84_key)


def main():
    ThreadAlice().start()
    ThreadBank().start()


if __name__ == "__main__":
    # execute only if run as a script
    main()

