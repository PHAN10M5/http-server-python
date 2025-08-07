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
            # Read raw bytes first
            request = b""
            while b"\r\n\r\n" not in request:
                chunk = connection.recv(1024)
                if not chunk:
                    break
                request += chunk

            if not request:
                connection.close()
                return

            # Decode headers only
            header_part = request.decode().split("\r\n\r\n")[0]
            lines = header_part.split("\r\n")
            request_line = lines[0]
            method, path, version = request_line.split(" ")

            # Default response
            response = "HTTP/1.1 404 Not Found\r\n\r\n"

            # Extract headers
            headers = {}
            for line in lines[1:]:
                if ":" in line:
                    key, value = line.split(":", 1)
                    headers[key.strip().lower()] = value.strip()

            # Extract body (partial or full)
            header_end = request.find(b"\r\n\r\n")
            body = request[header_end + 4:]

            if method == "GET":
                if path == "/":
                    response = "HTTP/1.1 200 OK\r\n\r\n"
                elif path == "/user-agent":
                    user_agent = headers.get("user-agent", "")
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
                    accept_encoding = headers.get("accept-encoding", "")
                    supports_gzip = "gzip" in accept_encoding.lower()

                    status_line = "HTTP/1.1 200 OK\r\n"
                    content_type = "Content-Type: text/plain\r\n"
                    content_encoding = "Content-Encoding: gzip\r\n" if supports_gzip else ""
                    content_length = f"Content-Length: {len(content.encode())}\r\n"
                    blank_line = "\r\n"

                    response = (
                        status_line +
                        content_type +
                        content_encoding +
                        content_length +
                        blank_line +
                        content
                    )


                elif path.startswith("/files/") and self.directory:
                    filename = path[len("/files/"):]
                    file_path = os.path.join(self.directory, filename)
                    if os.path.isfile(file_path):
                        with open(file_path, "rb") as f:
                            file_data = f.read()
                        header = (
                            "HTTP/1.1 200 OK\r\n"
                            "Content-Type: application/octet-stream\r\n"
                            f"Content-Length: {len(file_data)}\r\n"
                            "\r\n"
                        ).encode()
                        connection.sendall(header + file_data)
                        connection.close()
                        return
                    else:
                        response = "HTTP/1.1 404 Not Found\r\n\r\n"

            elif method == "POST" and path.startswith("/files/") and self.directory:
                filename = path[len("/files/"):]
                file_path = os.path.join(self.directory, filename)

                content_length = int(headers.get("content-length", 0))

                # Read more if body is incomplete
                while len(body) < content_length:
                    body += connection.recv(1024)

                # Save file
                with open(file_path, "wb") as f:
                    f.write(body)

                response = "HTTP/1.1 201 Created\r\n\r\n"

            connection.sendall(response.encode() if isinstance(response, str) else response)

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
