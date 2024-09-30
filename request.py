"""
Author: Sri Sasmi Polu
File name: request.py
Created: September 2024
Python Version: 3.10
"""
import json
from datetime import datetime, timezone


class BinaryTree:
    def __init__(self, root_obj):
        self.key = root_obj
        self.left_child = None
        self.right_child = None
        self.actions = None

    def insert_left(self, new_node):
        if self.left_child is None:
            self.left_child = BinaryTree(new_node)
        else:
            t = BinaryTree(new_node)
            t.left_child = self.left_child
            self.left_child = t

    def insert_right(self, new_node):
        if self.right_child is None:
            self.right_child = BinaryTree(new_node)
        else:
            t = BinaryTree(new_node)
            t.right_child = self.right_child
            self.right_child = t

    def perform_actions(self):
        if self.actions:
            print(f"Actions for {self.key}:")
            for i, action in enumerate(self.actions, start=1):
                print(f"\t{i}. {action}")
            action_choice = int(input("Select an action to perform (or 0 to go back): "))
            while action_choice > len(self.actions):
                action_choice = int(input("Please reselect the correct action to perform (or 0 to go back): "))

            if action_choice != 0:
                command = self.actions[action_choice - 1]
            else:
                command = None
            return action_choice, command


def navigate_tree(tree, client_socket):
    current_node = tree
    breadcrumbs = []  # Keep track of navigation to allow going back up the tree

    while current_node is not None:
        print(f"\nCurrent Menu: {current_node.key}")
        if current_node.left_child or current_node.right_child:
            choices = []
            if current_node.left_child:
                choices.append(current_node.left_child)
            if current_node.right_child:
                choices.append(current_node.right_child)

            print("Menu Options:")
            for i, child in enumerate(choices, start=1):
                print(f"\t{i}. {child.key}")
            print("\t0. Go back")

            choice = int(input("Enter your choice: "))
            if choice == 0:
                if len(breadcrumbs) == 0:
                    current_node = None
                else:
                    current_node = breadcrumbs.pop()
            elif 0 < choice <= len(choices):
                next_node = choices[choice - 1]
                breadcrumbs.append(current_node)  # Add to breadcrumbs before going deeper
                current_node = next_node
            else:
                print("Invalid selection, please try again.")
        else:
            action_choice, command = current_node.perform_actions()
            if action_choice == 0:
                if len(breadcrumbs) == 0:
                    current_node = None
                else:
                    current_node = breadcrumbs.pop()
            else:
                if command == "ADD_SONG":
                    server_data, song_id = add_song_request(command, client_socket)
                    if server_data == "None":
                        server_data = f"Song ID: {song_id} is not in catalog. Please Retry."
                elif command == "REMOVE_SONG":
                    server_data, song_id = remove_song_request(command, client_socket)
                    if server_data == "None":
                        server_data = f"Song ID: {song_id} is not in your playlist. Please Retry."
                elif command == "FIND_SONG":
                    server_data, song_id = find_song_request(command, client_socket)
                    if server_data == "None":
                        server_data = f"Song ID: {song_id} is not in your playlist."
                elif command == "SWITCH_PLAY":
                    server_data = "Switched from 'Design' mode to 'Play' mode"
                    current_node = tree.right_child.right_child  # play node
                    pm = set_play_mode("SET_PLAY_MODE", client_socket)
                    command_dict = {
                        "header": get_header(),
                        "command": command,
                        "args": {}
                    }
                    send_data = json.dumps(command_dict)
                    client_socket.send(send_data.encode())
                    current_playing_song = client_socket.recv(2048).decode()
                    server_data = server_data + "\n" + pm + "\n" + current_playing_song
                elif command == "QUIT":
                    server_data = "Closing the interactive terminal"
                    print(server_data)
                    break
                elif command == "SET_PLAY_MODE":
                    server_data = set_play_mode(command, client_socket)
                elif command == "STOP":
                    current_node = tree.right_child.left_child  # design node
                    command_dict = {
                        "header": get_header(),
                        "command": command,
                        "args": {}
                    }
                    send_data = json.dumps(command_dict)
                    client_socket.send(send_data.encode())
                    server_data = client_socket.recv(2048).decode()
                else:
                    args = {}
                    print(f"\nPerforming '{command}' action.")
                    command_dict = {
                        "header": get_header(),
                        "command": command,
                        "args": args
                    }
                    send_data = json.dumps(command_dict)
                    client_socket.send(send_data.encode())
                    server_data = client_socket.recv(2048).decode()

                print(f"Server reply: {server_data}")


def get_header():
    header_value = {
        "user": "Sri Sasmi Polu",
        "GWID": "G40795997",
        "request_time": datetime.now(timezone.utc).strftime("%y-%m-%d::%H:%M:%S"),
        "client_ip": "127.0.0.1",
        "server_addr": "127.0.0.1:12000"
    }
    return header_value


def add_song_request(command, client_socket):
    add_song_id = int(input("ID of song to add: "))
    args = {"id": add_song_id}
    print(f"\nPerforming '{command}' action.")
    command_dict = {
        "header": get_header(),
        "command": command,
        "args": args
    }
    send_data = json.dumps(command_dict)
    client_socket.send(send_data.encode())
    server_data = client_socket.recv(2048).decode()
    return server_data, add_song_id


def remove_song_request(command, client_socket):
    remove_song_id = int(input("ID of song to remove: "))
    args = {"id": remove_song_id}
    print(f"\nPerforming '{command}' action.")
    command_dict = {
        "header": get_header(),
        "command": command,
        "args": args
    }
    send_data = json.dumps(command_dict)
    client_socket.send(send_data.encode())
    server_data = client_socket.recv(2048).decode()
    return server_data, remove_song_id


def find_song_request(command, client_socket):
    add_song_id = int(input("ID of song to find: "))
    args = {"id": add_song_id}
    print(f"\nPerforming '{command}' action.")
    command_dict = {
        "header": get_header(),
        "command": command,
        "args": args
    }
    send_data = json.dumps(command_dict)
    client_socket.send(send_data.encode())
    server_data = client_socket.recv(2048).decode()
    return server_data, add_song_id


def set_play_mode(command, client_socket):
    print("Please select a play mode from below: ")
    print("\t1. Default\n\t2. Shuffle\n\t3. Loop")
    play_mode = int(input("Enter play mode ID: "))
    while play_mode not in [1, 2, 3]:
        print("Please select a valid play mode.")
        play_mode = int(input("Re-enter play mode ID: "))
    if play_mode == 1:
        args = {"play_mode": "default"}
    elif play_mode == 2:
        args = {"play_mode": "shuffle"}
    else:  # play_model == 3
        args = {"play_mode": "loop"}

    print(f"\nPerforming '{command}' action.")
    command_dict = {
        "header": get_header(),
        "command": command,
        "args": args
    }
    send_data = json.dumps(command_dict)
    client_socket.send(send_data.encode())
    server_data = client_socket.recv(2048).decode()
    return server_data
