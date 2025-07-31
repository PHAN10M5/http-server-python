import socket
from sqlite3 import Connection  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    #Uncomment this to pass the first stage
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept()
    
    request = connection.recv(1024).decode()

    lines = request.split("\r\n")
    request_line = lines[0]
    method, path, version = request_line.split(" ")

    user_agent = ""
    for line in lines:
        if line.startswith("User-Agent: "):
            user_agent = line[len("User-Agent: ")]

    response = "HTTP/1.1 404 Not Found\r\n\r\n"
    
    if method == "GET":
        if path == "/":
            response = "HTTP/1.1 200 OK\r\n\r\n"
        elif path == "/user-agent":
            content_length = len(user_agent.encode())
            response = (
                "HTTP/1.1 200 OK\r\n\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {content_length}\r\n"
                "\r\n"
                f"{user_agent}"
            )
        elif path.startswith("/echo/"):
            echo_string = path[len("/echo/"):]
            content_length = len(echo_string.encode())
            response = (
                "HTTP/1.1 200 OK\r\n\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {content_length}\r\n"
                "\r\n"
                f"{echo_string}"
            )

    connection.sendall(response.encode())
    connection.close()

if __name__ == "__main__":
    main()
