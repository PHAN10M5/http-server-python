import socket
from sqlite3 import Connection  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    #Uncomment this to pass the first stage
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept()
    
    request =connection.recv(1024).decode()

    lines = request.split("\r\n")
    print(lines)
    request_line = lines[0]
    headers = lines[1:]

    parts = request_line.split(" ")
    method = parts[0]
    path = parts[1]

    for header in headers:
        if header.lower().startswith("user-agent:"):
            user_agent = header.split(": ")[1]
            break

    print(user_agent)

    if method == "GET" and path == "/user-agent":
        content_length = len(user_agent)
        response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {content_length}\r\n"
                "\r\n"
                f"{user_agent}"
            )
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
    print(response)
    connection.sendall(response.encode())
    connection.close()

if __name__ == "__main__":
    main()
