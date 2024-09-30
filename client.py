"""
Author: Sri Sasmi Polu
File name: client.py
Created: September 2024
Python Version: 3.10
"""
import socket

from request import BinaryTree, navigate_tree

HOST = "127.0.0.1"  # Server address
PORT = 12000  # Server port


# Menu for navigation
MENU = BinaryTree("Main Menu")
# Main Left
MENU.insert_left("Catalog Menu")
MENU.left_child.actions = ["REQUEST_CATALOG"]
# Main Right
MENU.insert_right("Playlist Menu")
# Main Right Child Left
MENU.right_child.insert_left("Design")
MENU.right_child.left_child.actions = [
    "REQUEST_CATALOG", "REQUEST_PLAYLIST", "ADD_SONG", "REMOVE_SONG",
    "FIND_SONG", "SWITCH_PLAY", "QUIT"
]
# Main Right Child Right
MENU.right_child.insert_right("Play")
MENU.right_child.right_child.actions = [
    "REQUEST_PLAYLIST", "SET_PLAY_MODE", "NOW_PLAYING", "PLAY_NEXT",
    "GO_BACK", "STOP"
]


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    navigate_tree(MENU, s)
