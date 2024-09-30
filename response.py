"""
Author: Sri Sasmi Polu
File name: response.py
Created: September 2024
Python Version: 3.10
"""


def get_playlist_songs_string(catalog):
    all_songs = []
    for item in catalog:
        all_songs.append(f"ID: {item['id']}. Song: {item['song_title']}")
    return "\n".join(all_songs)


def find_song(list_of_songs, song_id):
    for item in list_of_songs:
        if song_id == item["id"]:
            return item
    return "None"


def find_song_index(list_of_songs, song_id):
    for i in range(len(list_of_songs)):
        item = list_of_songs[i]
        if song_id == item["id"]:
            return i
    return "None"
