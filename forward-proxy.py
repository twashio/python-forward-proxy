import socket
import sys
import threading


class Server:
    def __init__(self, buffer_size: int = 1024, listening_port: int = 8000, max_connection: int = 5) -> None:
        self.__socket = None
        self.__buffer_size = buffer_size
        self.__listening_port = listening_port
        self.__max_connection = max_connection

    # Start the server.
    def start(self) -> None:
        # Create a socket.
        try:
            self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__socket.bind(('', self.__listening_port))
            self.__socket.listen(self.__max_connection)
            print("[*] Server started: %d" % (self.__listening_port))
        except Exception as error:
            print("[*] Unable to Initialize ")
            print(error)
            sys.exit(1)

    # Establish a connection and relay communication.
    def accept(self) -> None:
        while True:
            try:
                conn, addr = self.__socket.accept()
                print("[*] Accept: %s:%d" % (addr[0], addr[1]))
                data = conn.recv(self.__buffer_size)

                t = threading.Thread(
                    target=self.proxy, args=(conn, data))  # Create a thread.
                t.start()  # Start the thread.

            except KeyboardInterrupt:
                self.__socket.close()
                print("\n[*] Shutdown")
                sys.exit(0)

    # Proxy the request and forward results.
    def proxy(self, conn, data) -> None:
        print(data)

       # Parse the request and extract server's address and port number.
        webserver, port = self.parse_request(data)

        try:
            # Create a socket to communicate with the web server.
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((webserver, port))  # Establish a connection with the web server.
            sock.send(data)  # Send data to the web server.

            while True:
                reply = sock.recv(self.__buffer_size)  # Recieve response from the web server.
                if (len(reply) > 0):
                    conn.send(reply)
                else:
                    break

            sock.close()  # Close the connection with the web server.
            conn.close()  # Close the connection with the client.

        except Exception as error:
            sock.close()
            conn.close()
            print(error)
            sys.exit(1)

    # HTTPリクエストの解析
    def parse_request(self, data) -> (str, int):
        try:
            first_line = data.split(b'\n')[0]  # Extract the first line of the request.
            url = first_line.split()[1]  # # Extract the URL.

            http_pos = url.find(b'://')  # Find the positiion of "://".
            if (http_pos == -1):
                tmp = url
            else:
                tmp = url[(http_pos+3):]  # Extract everything after "://".

            port_pos = tmp.find(b':')  # Find the position of the ":".
            webserver_pos = tmp.find(b'/')  # Find the position of the "/".

            if webserver_pos == -1:
                webserver_pos = len(tmp)
            webserver = ""
            port = -1
            if (port_pos == -1):  # If the web server is using port 80.
                port = 80
                webserver = tmp[:webserver_pos]
            else:  # If the web server is not using port 80.
                port = int(tmp[port_pos+1:][:webserver_pos-port_pos-1])
                webserver = tmp[:port_pos]

            return webserver, port

        except Exception as error:
            print(error)
            sys.exit(1)


if __name__ == '__main__':
    server = Server()
    server.start()
    server.accept()
