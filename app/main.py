import socket
import threading
import sys
import os
import gzip


class TCPServer:
    def __init__(self, host="localhost", port=4221, directory=None):
        self.host = host
        self.port = port
        self.directory = directory
        self.server_socket = socket.create_server((self.host, self.port), reuse_port=True)

    def start(self):
        print(f"Server started on {self.host}:{self.port}, serving from {self.directory}")
        while True:
            conn, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(conn, addr)).start()

    def handle_client(self, connection, address):
        try:
            while True:
                request_data = self.receive_http_request(connection)
                if not request_data:
                    break

                method, path, headers, body = self.parse_http_request(request_data)
                response = self.route_request(method, path, headers, body)
                connection.sendall(response)

                if headers.get("connection", "").lower() == "close":
                    break
        except Exception as e:
            print("Error handling client:", e)
        finally:
            connection.close()

    def receive_http_request(self, connection):
        """Read request until headers are complete, then read body if needed."""
        request = b""
        while b"\r\n\r\n" not in request:
            chunk = connection.recv(1024)
            if not chunk:
                return None
            request += chunk

        header_end = request.find(b"\r\n\r\n")
        headers_raw = request[:header_end].decode(errors="replace")
        headers_lines = headers_raw.split("\r\n")
        method, path, version = headers_lines[0].split(" ")

        headers = {}
        for line in headers_lines[1:]:
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip().lower()] = v.strip()

        body = request[header_end + 4:]
        content_length = int(headers.get("content-length", 0))
        while len(body) < content_length:
            body += connection.recv(1024)

        return method, path, headers, body

    def parse_http_request(self, request_data):
        """Just unpack the tuple for clarity."""
        return request_data

    def route_request(self, method, path, headers, body):
        """Match request to handler."""
        if method == "GET":
            if path == "/":
                return self.http_response(200, b"", "text/plain")

            elif path == "/user-agent":
                user_agent = headers.get("user-agent", "")
                return self.http_response(200, user_agent.encode(), "text/plain")

            elif path.startswith("/echo/"):
                text = path[len("/echo/"):]
                if "gzip" in headers.get("accept-encoding", "").lower():
                    compressed = gzip.compress(text.encode())
                    return self.http_response(200, compressed, "text/plain", extra_headers={"Content-Encoding": "gzip"})
                else:
                    return self.http_response(200, text.encode(), "text/plain")

            elif path.startswith("/files/") and self.directory:
                filename = path[len("/files/"):]
                file_path = os.path.join(self.directory, filename)
                if os.path.isfile(file_path):
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                    return self.http_response(200, file_data, "application/octet-stream")
                else:
                    return b"HTTP/1.1 404 Not Found\r\n\r\n"

        elif method == "POST" and path.startswith("/files/") and self.directory:
            filename = path[len("/files/"):]
            file_path = os.path.join(self.directory, filename)
            with open(file_path, "wb") as f:
                f.write(body)
            return b"HTTP/1.1 201 Created\r\n\r\n"

        return b"HTTP/1.1 400 Bad Request\r\n\r\n"

    def http_response(self, status_code, body, content_type, extra_headers=None):
        """Build an HTTP response."""
        reason = {200: "OK", 201: "Created", 400: "Bad Request", 404: "Not Found"}.get(status_code, "OK")
        headers = {
            "Content-Type": content_type,
            "Content-Length": str(len(body))
        }
        if extra_headers:
            headers.update(extra_headers)

        header_str = "".join(f"{k}: {v}\r\n" for k, v in headers.items())
        return f"HTTP/1.1 {status_code} {reason}\r\n{header_str}\r\n".encode() + body


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
