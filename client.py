import threading
import socket
from datetime import datetime

port = 55555

print("Press ^C to exit.")

host = input("Please enter the IP of the host: ")

nickname = input("Choose a nickname: ")
if nickname == "admin":
    password = input("Please enter admin password: ")

client = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
client.connect((host, port))

stop_thread = False

def receive():
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            message = client.recv(1024).decode("ascii")
            if message == "NICK":
                client.send(nickname.encode("ascii"))
                next_message = client.recv(1024).decode("ascii")
                if next_message == "PASS":
                    client.send(password.encode("ascii"))
                    if client.recv(1024).decode("ascii") == "REFUSE":
                        print("Wrong password! If you are not an admin and trying to get in I will come to your house.")
                        stop_thread = True
                elif next_message == "BAN":
                    print("You are banned!")
                    client.close()
                    stop_thread = True
            else:
                print(message)
        except:
            print("An error occurred!")
            client.close()
            break

def write():
    while True:
        if stop_thread:
            break
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        message = f"{current_time} <{nickname}>: {input('')}"
        if message[len(current_time)+len(nickname)+5:].startswith("/"):
            if nickname == "admin":
                if message[len(current_time)+len(nickname)+5:].startswith("/kick"):
                    client.send(f"KICK {message[len(current_time)+len(nickname)+5+6:]}".encode("ascii"))
                elif message[len(current_time)+len(nickname)+5:].startswith("/ban"):
                    client.send(f"BAN {message[len(current_time)+len(nickname)+5+5:]}".encode("ascii"))
            else:
                print("You do not have permission to execute this command!")
        else:
            client.send(message.encode("ascii"))

receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
