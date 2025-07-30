import socket
from sqlite3 import Connection  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    #Uncomment this to pass the first stage
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept()
    print("Client connected")
    
    request =connection.recv(1024).decode()

    request_lines = request.split(" ")
    method = request_lines[0]
    path = request_lines[1]
    version = request_lines[2]

    if path == "/":
        response = "HTTP/1.1 200 OK\r\n\r\n"
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"

    print(response)
    connection.sendall(response.encode())
    connection.close()

if __name__ == "__main__":
    main()
