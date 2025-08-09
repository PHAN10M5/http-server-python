import socket
import threading
import sys
import os
import gzip


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
            while True:  # loop to handle multiple requests per connection
                # Read request headers fully
                request = b""
                while b"\r\n\r\n" not in request:
                    chunk = connection.recv(1024)
                    if not chunk:
                        return  # client closed connection
                    request += chunk

                if not request.strip():
                    return  # no request, close

                # Parse request
                header_part = request.decode(errors="replace").split("\r\n\r\n")[0]
                lines = header_part.split("\r\n")
                request_line = lines[0]
                method, path, version = request_line.split(" ")

                headers = {}
                for line in lines[1:]:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        headers[key.strip().lower()] = value.strip()

                # Read body if needed
                header_end = request.find(b"\r\n\r\n")
                body = request[header_end + 4:]
                content_length = int(headers.get("content-length", 0))
                while len(body) < content_length:
                    body += connection.recv(1024)

                # Handle request (same as before)
                response = self.handle_request(method, path, headers, body, connection)

                # Send response
                if response:
                    connection.sendall(response)

                # Close if client said so
                if headers.get("connection", "").lower() == "close":
                    break

        except Exception as e:
            print("Error:", e)
        finally:
            connection.close()


    def handle_request(self, method, path, headers, body, connection):
        if method == "GET":
            if path == "/":
                content = b""
                response = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: text/plain\r\n"
                    f"Content-Length: {len(content)}\r\n"
                    f"\r\n"
                ).encode() + content


            elif path == "/user-agent":
                user_agent = headers.get("user-agent", "")
                content = user_agent
                response = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Content-Type: text/plain\r\n"
                    f"Content-Length: {len(content)}\r\n"
                    f"\r\n"
                ).encode() + content.encode()

            elif path.startswith("/echo/"):
                content = path[len("/echo/"):]
                accept_encoding = headers.get("accept-encoding", "")
                supports_gzip = "gzip" in accept_encoding.lower()

                if supports_gzip:
                    compressed_content = gzip.compress(content.encode())
                    response = (
                        f"HTTP/1.1 200 OK\r\n"
                        f"Content-Type: text/plain\r\n"
                        f"Content-Encoding: gzip\r\n"
                        f"Content-Length: {len(compressed_content)}\r\n"
                        f"\r\n"
                    ).encode() + compressed_content
                else:
                    response = (
                        f"HTTP/1.1 200 OK\r\n"
                        f"Content-Type: text/plain\r\n"
                        f"Content-Length: {len(content)}\r\n"
                        f"\r\n"
                    ).encode() + content.encode()

            elif path.startswith("/files/") and self.directory:
                filename = path[len("/files/"):]
                file_path = os.path.join(self.directory, filename)
                if os.path.isfile(file_path):
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                    header = (
                        f"HTTP/1.1 200 OK\r\n"
                        f"Content-Type: application/octet-stream\r\n"
                        f"Content-Length: {len(file_data)}\r\n"
                        f"\r\n"
                    ).encode()
                    connection.sendall(header + file_data)
                    return
                else:
                    response = b"HTTP/1.1 404 Not Found\r\n\r\n"

        elif method == "POST" and path.startswith("/files/") and self.directory:
            filename = path[len("/files/"):]
            file_path = os.path.join(self.directory, filename)

            content_length = int(headers.get("content-length", 0))
            while len(body) < content_length:
                body += connection.recv(1024)

            with open(file_path, "wb") as f:
                f.write(body)

            response = b"HTTP/1.1 201 Created\r\n\r\n"

        connection.sendall(response)
        return response


def main():
    directory = None
    if "--directory" in sys.argv:
        dir_index = sys.argv.index("--directory") + 1
        if dir_index < len(sys.argv):
            directory = sys.argv[dir_index]

    server = TCPServer(directory=directory)
    server.start()


if __name__ == "__main__":
    main()
