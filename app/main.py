import socket
import threading


class TCPServer():
    def __init__(self, host='localhost', port=4221):
        self.host = host
        self.port = port
        self.server_socket = socket.create_server((self.host, self.port), reuse_port=True)

    def start(self):
        print(f"Server started on {self.host}:{self.port}")
        while True:
            connection, address = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(connection, address)).start()

    def handle_client(self, connection, address):
        print(f"Connection from {address}")
        request = connection.recv(1024).decode()

        lines = request.split("\r\n")
        request_line = lines[0]
        method, path, version = request_line.split(" ")

        user_agent = ""
        for line in lines:
            if line.startswith("User-Agent: "):
                user_agent = line[len("User-Agent: "):]

        print(user_agent)

        response = "HTTP/1.1 404 Not Found\r\n\r\n"
        
        if method == "GET":
            if path == "/":
                response = "HTTP/1.1 200 OK\r\n\r\n"
            elif path == "/user-agent":
                content_length = len(user_agent.encode())
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/plain\r\n"
                    f"Content-Length: {content_length}\r\n"
                    "\r\n"
                    f"{user_agent}"
                )
            elif path.startswith("/echo/"):
                echo_string = path[len("/echo/"):]
                content_length = len(echo_string.encode())
                response = (
                    "HTTP/1.1 200 OK\r\n"
                    "Content-Type: text/plain\r\n"
                    f"Content-Length: {content_length}\r\n"
                    "\r\n"
                    f"{echo_string}"
                )
        print(response)
        connection.sendall(response.encode())
        connection.close()


if __name__ == "__main__":
    server = TCPServer()
    server.start()
