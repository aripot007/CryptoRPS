import secrets
import socket
import hashlib

choices_str = ["Rock", "Paper", "Scissors"]

print("   _____                  _        _____  _____   _____")
print("  / ____|                | |      |  __ \\|  __ \\ / ____|")
print(" | |     _ __ _   _ _ __ | |_ ___ | |__) | |__) | (___")
print(" | |    | '__| | | | '_ \\| __/ _ \\|  _  /|  ___/ \\___ \\")
print(" | |____| |  | |_| | |_) | || (_) | | \\ \\| |     ____) |")
print("  \\_____|_|   \\__, | .__/ \\__\\___/|_|  \\_\\_|    |_____/ ")
print("               __/ | |")
print("              |___/|_|                                  ")

print("\nA Cryptographically secure Rock-Paper-Scissors game, because why not\n\n")


print("Please pick a connection option : ")
print("[1] Host a game")
print("[2] Connect to a game")
print("")

while True:
    choice = input("Choice : ")

    if choice == "1":
        server_mode = True
        break

    elif choice == "2":
        server_mode = False
        break

    print("Please enter a valid choice !")

s = None
c = None

if server_mode:
    while True:
        port = input("Listen on port [4242] :")

        if port == "":
            port = 4242
        elif port.isnumeric():
            port = int(port)
        else:
            print("Please enter a valid port")
            continue

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind(("", port))
            break
        except Exception as e:
            print("Error while binding socket, maybe the port is already in use ?")
            print(e)

    print(f"Waiting for connection on port {port} ...")

    s.listen(1)
    c, addr = s.accept()

    print(f"Received connection from {addr} !")

else:
    while True:
        host = input("Host : ")
        port = input("Port [4242] : ")

        if port == "":
            port = 4242
        elif port.isnumeric():
            port = int(port)
        else:
            print("Please enter a valid port !")
            continue

        print(f"Connecting to {host}:{port} ... ")

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            break
        except Exception as e:
            print("Error while connecting to host !")
            print(e)
            continue

    print("Connected successfully !")

    c = s


def make_choice():
    print("Please pick an option : ")
    print("[1] Rock")
    print("[2] Paper")
    print("[3] Scissors")

    while True:
        choice = input("choice : ")
        if choice in ["1", "2", "3"]:
            return int(choice)
        print("Please enter a valid choice !")


try:
    while True:

        choice = make_choice()

        r1 = secrets.token_bytes(256)
        r2 = secrets.token_bytes(256)

        choice_bytes = choice.to_bytes(1, "little")

        msg = r1 + r2 + choice_bytes

        # Send the commitment
        c.sendall(hashlib.sha512(msg).digest())
        c.sendall(r1)

        print("Waiting for other player ... ")

        commitment = c.recv(64)
        other_r1 = c.recv(256)

        print("Validating choices ... ")

        c.sendall(msg)
        other_msg = c.recv(513)

        if other_msg[0:256] != other_r1 or hashlib.sha512(other_msg).digest() != commitment:
            print("Invalid commitment, the other player might have tried to cheat !")
            print("Ending game ... ")
            break

        other_choice = other_msg[-1]

        print("")

        print(f"Your choice : {choices_str[choice - 1]}")
        print(f"Opponent's choice : {choices_str[other_choice - 1]}")
        print("")

        win = 0
        if choice == 1:
            if other_choice == 2:
                win = -1
            elif other_choice == 3:
                win = 1

        elif choice == 2:
            if other_choice == 3:
                win = -1
            if other_choice == 1:
                win = 1

        else:
            if other_choice == 1:
                win = -1
            elif other_choice == 2:
                win = 1

        if win == 1:
            print("You won !")
        elif win == -1:
            print("You lost !")
        else:
            print("Draw !")

        next_game = input("\nContinue ? [Y/n] : ")
        if next_game.lower() == "n":
            break

    print("Exiting ... ")
    c.close()
    if server_mode:
        s.close()
    exit(0)

except ConnectionError as e:
    print("A connection error occured : ")
    print(e)

