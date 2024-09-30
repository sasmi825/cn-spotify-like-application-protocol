"""
Author: Sri Sasmi Polu
File name: server.py
Created: September 2024
Python Version: 3.10
"""
import copy
import json
import socket
from random import shuffle

from response import get_playlist_songs_string, find_song, find_song_index

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 12000 # Port to listen on

print("Loading the song catalog")
_catalog_ = json.load(open("database.json", "r"))
CATALOG = _catalog_["catalog"]  # list[dict[str, str]]
print("Loading the playlist")
PLAYLIST = []
OG_PLAYLIST = []
PREV_SONG = None
PLAY_MODE = "default"


def get_current_song():
    global PLAYLIST
    return PLAYLIST[0]


def handle_client_data(client_data):
    global CATALOG
    global PLAYLIST
    global OG_PLAYLIST
    global PREV_SONG
    global PLAY_MODE

    client_dict = json.loads(client_data)
    command = client_dict["command"]

    if "header" in client_dict.keys():
        header_print = f"Request Time: {client_dict['header']['request_time']}; User: {client_dict['header']['user']};"
    else:
        header_print = ""

    # Handle command
    if command == "REQUEST_CATALOG":
        # _catalog_human_readable_
        print(f"{header_print} Message: Sending entire catalog to client.")
        return get_playlist_songs_string(CATALOG).encode()
    elif command == "REQUEST_PLAYLIST":
        print(f"{header_print} Message: Sending entire playlist to client.")
        if len(PLAYLIST) == 0:
            return "There are no songs in your playlist.".encode()
        else:
            return get_playlist_songs_string(PLAYLIST).encode()
    elif command == "ADD_SONG":
        print(f"{header_print} Message: Trying to add a song to the playlist")
        song_id = client_dict["args"]["id"]
        song = find_song(CATALOG, song_id)
        if isinstance(song, dict):
            PLAYLIST.append(song)
            print(f"{header_print} Message: Add song {song_id} successful.")
            return f"Song ID {song_id} added to the playlist.".encode()
        else:
            return "None".encode()
    elif command == "REMOVE_SONG":
        print(f"{header_print} Message: Trying to remove a song from the playlist")
        song_id = client_dict["args"]["id"]
        remove_idx = find_song_index(PLAYLIST, song_id)
        if isinstance(remove_idx, int):
            PLAYLIST.pop(remove_idx)
            print(f"{header_print} Message: Remove song {song_id} successful")
            return f"Song ID {song_id} removed from the playlist.".encode()
        else:
            return "None".encode()
    elif command == "FIND_SONG":
        print(f"{header_print} Message: Trying to find a song in the playlist")
        song_id = client_dict["args"]["id"]
        song = find_song(PLAYLIST, song_id)
        if isinstance(song, dict):
            song_str = get_playlist_songs_string([song])
            print(f"{header_print} Message: Found song {song_id}")
            return f"Found the song in your playlist: {song_str}".encode()
        else:
            return "None".encode()
    elif command == "SWITCH_PLAY":
        print(f"{header_print} Message: Switching from design mode to play mode")
        if len(PLAYLIST) == 0:
            return "There are no songs in your playlist.".encode()
        else:
            OG_PLAYLIST = copy.deepcopy(PLAYLIST)
            # PLAY_MODE = client_dict["args"]["play_mode"]
            song = get_current_song()
            song_str = get_playlist_songs_string([song])
            return f"Current playing song: {song_str}".encode()
    elif command == "SET_PLAY_MODE":
        print(f"{header_print} Message: Setting a play mode.")
        PLAY_MODE = client_dict["args"]["play_mode"]
        if PLAY_MODE == "shuffle":
            # OG_PLAYLIST = copy.deepcopy(PLAYLIST)
            shuffle(PLAYLIST)
        return f"Setting play mode to: {PLAY_MODE}".encode()
    elif command == "NOW_PLAYING":
        print(f"{header_print} Message: Finding current song that is being played.")
        if len(PLAYLIST) == 0:
            return "There are no songs in your playlist.".encode()
        else:
            song = get_current_song()
            song_str = get_playlist_songs_string([song])
            return f"Current playing song: {song_str}".encode()
    elif command == "PLAY_NEXT":
        print(f"{header_print} Message: Playing next song.")
        if len(PLAYLIST) == 0:
            return "There are no songs in your playlist.".encode()
        else:
            PREV_SONG = PLAYLIST[0]
            PLAYLIST = PLAYLIST[1:]
            if len(PLAYLIST) == 0:
                return "There are no songs in your playlist.".encode()
            if PLAY_MODE == "loop":
                PLAYLIST.append(PREV_SONG)
            song = PLAYLIST[0]
            song_str = get_playlist_songs_string([song])
            return f"Current playing song: {song_str}".encode()
    elif command == "GO_BACK":
        print(f"{header_print} Message: Playing previous song.")
        if PREV_SONG is None:
            return "There are no previous songs to go back.".encode()
        else:
            if PLAY_MODE == "loop":
                PLAYLIST = [PREV_SONG] + PLAYLIST[:-1]
            else:
                PLAYLIST = [PREV_SONG] + PLAYLIST
            PREV_SONG = None
            song = PLAYLIST[0]
            song_str = get_playlist_songs_string([song])
            return f"Current playing (previous) song: {song_str}".encode()
    elif command == "STOP":
        print(f"{header_print} Message: Switching from play mode to design mode")
        PLAYLIST = copy.deepcopy(OG_PLAYLIST)
        return f"Switched from 'Play' mode to 'Design' mode".encode()
    else:
        print(f"{header_print} Message: Invalid command '{command}'")
        return f"Invalid command".encode()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f'Server listening on {HOST}:{PORT}')

    # conn is client socket object. It is different from s socket
    conn, addr = s.accept()
    with conn:
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            print(f"Client address: {addr}")
            # process data
            send_data = handle_client_data(data)
            # send data
            conn.send(send_data)
