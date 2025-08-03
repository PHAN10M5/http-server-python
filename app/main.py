import socket
import threading
import sys
import os


class TCPServer:
    def __init__(self, host='localhost', port=4221, directory=None):
        self.host = host
        self.port = port
        self.directory = directory
        self.server_socket = socket.create_server((self.host, self.port), reuse_port=True)

    def start(self):
        print(f"Server started on {self.host}:{self.port}, serving from {self.directory}")
        while True:
            connection, address = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(connection, address)).start()

    def handle_client(self, connection, address):
        try:
            request = connection.recv(1024).decode()
            if not request:
                connection.close()
                return

            lines = request.split("\r\n")
            request_line = lines[0]
            method, path, version = request_line.split(" ")

            # Extract User-Agent if present
            user_agent = ""
            for line in lines:
                if line.startswith("User-Agent: "):
                    user_agent = line[len("User-Agent: "):]

            # Default 404 response
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

            if method == "GET":
                if path == "/":
                    response = "HTTP/1.1 200 OK\r\n\r\n"
                elif path == "/user-agent":
                    content = user_agent
                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        f"Content-Length: {len(content.encode())}\r\n"
                        "\r\n"
                        f"{content}"
                    )
                elif path.startswith("/echo/"):
                    content = path[len("/echo/"):]
                    response = (
                        "HTTP/1.1 200 OK\r\n"
                        "Content-Type: text/plain\r\n"
                        f"Content-Length: {len(content.encode())}\r\n"
                        "\r\n"
                        f"{content}"
                    )
                elif path.startswith("/files/") and self.directory:
                    filename = path[len("/files/"):]
                    file_path = os.path.join(self.directory, filename)

                    if os.path.isfile(file_path):
                        with open(file_path, "rb") as f:
                            file_data = f.read()
                        response = (
                            "HTTP/1.1 200 OK\r\n"
                            "Content-Type: application/octet-stream\r\n"
                            f"Content-Length: {len(file_data)}\r\n"
                            "\r\n"
                        ).encode() + file_data
                        connection.sendall(response)
                        connection.close()
                        return
                    else:
                        response = "HTTP/1.1 404 Not Found\r\n\r\n"

            connection.sendall(response.encode())
        except Exception as e:
            print("Error:", e)
        finally:
            connection.close()


def main():
    # Default directory = None
    directory = None

    # Read --directory argument from command line
    if "--directory" in sys.argv:
        dir_index = sys.argv.index("--directory") + 1
        if dir_index < len(sys.argv):
            directory = sys.argv[dir_index]

    server = TCPServer(directory=directory)
    server.start()


if __name__ == "__main__":
    main()
