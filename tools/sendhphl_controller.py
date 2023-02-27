import socket


def main():
    ip = 'localhost'
    port = 12349
    # connect to a tcp socket
    # send the character 'P' to the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    sock.send(b'P')
    sock.close()
