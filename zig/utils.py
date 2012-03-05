from functools import wraps
import binascii
import zmq


def coro(func):
    @wraps(func)
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        cr.next()
        return cr
    return start


def dump(msg_or_socket):
    # from zguide zhelpers
    if isinstance(msg_or_socket, zmq.Socket):
        # it's a socket, call on current message
        return dump(msg_or_socket.recv_multipart())
    else:
        msg = msg_or_socket
    print "----------------------------------------"
    for part in msg:
        print "[%03d]" % len(part),
        is_text = True
        for c in part:
            if ord(c) < 32 or ord(c) > 128:
                is_text = False
                break
        if is_text:
            # print only if ascii text
            print part
        else:
            # not text, print hex
            print binascii.hexlify(part)
