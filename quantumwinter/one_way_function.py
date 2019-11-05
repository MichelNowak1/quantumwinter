from cqc.pythonLib import CQCConnection, qubit


def one_way_function(conn, BB84_key, db_id, r, M):
    owf_state = qubit(conn)
    owf_key = bin(BB84_key)[2:] + bin(db_id)[2:] + bin(r)[2:] + bin(M)[2:]
    owf_key = int(abs(hash(str(owf_key))))%256
    print(owf_key)
    owf_state.rot_X(owf_key)
    return owf_state
