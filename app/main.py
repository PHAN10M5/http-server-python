import socket
from sqlite3 import Connection  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    #Uncomment this to pass the first stage
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    connection, address = server_socket.accept()
    
    request =connection.recv(1024).decode()

    request_lines = request.split(" ")
    method = request_lines[0]
    path = request_lines[1]
    user_agent = request_lines[5].split("\r\n")[0]

    print(user_agent)
    response = "HTTP/1.1 404 Not Found\r\n\r\n"

    if method == "GET":
        
        if user_agent:
            content_length = len(user_agent)
            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/plain\r\n"
                f"Content-Length: {content_length}\r\n"
                "\r\n"
                f"{user_agent}"
            )


    print(response)
    connection.sendall(response.encode())
    connection.close()

if __name__ == "__main__":
    main()
