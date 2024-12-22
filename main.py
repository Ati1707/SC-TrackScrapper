import requests
import time
import re

from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from threading import Thread, Lock
from user_database import *

print_lock = Lock()

def get_user_id(permalink, client_id):
    url = f"https://api-v2.soundcloud.com/resolve?url=https://soundcloud.com/{permalink}&client_id={client_id}"
    response = requests.get(url)
    while response.status_code != 200:
        time.sleep(0.5)
        response = requests.get(url)
    return response.json()['id']


def get_followers(user_id, client_id):
    followers = []
    url = f"https://api-v2.soundcloud.com/users/{user_id}/followers?limit=200&client_id={client_id}"

    while url:
        response = requests.get(url)
        if response.status_code != 200:
            #print(f"Failed to get followers: {response.status_code}. Retrying...")
            time.sleep(0.5)
            continue

        data = response.json()
        for follower in data.get('collection', []):
            if follower.get('track_count', 0) > 0:
                followers.append(follower)
        url = data.get('next_href')
        if url:
            url = f"{url}&client_id={client_id}"

    return followers

def get_user_tracks(user_id, client_id):
    tracks = []
    url = f"https://api-v2.soundcloud.com/users/{user_id}/tracks?limit=5&linked_partitioning=true&client_id={client_id}"
    response = requests.get(url)
    while response.status_code != 200:
        response = requests.get(url)

    data = response.json()
    tracks.extend(data.get('collection', []))
    return tracks

def get_follower_details(follower_id, client_id):
    url = f"https://api-v2.soundcloud.com/users/{follower_id}?client_id={client_id}"
    response = requests.get(url)
    while response.status_code != 200:
        time.sleep(0.5)
        response = requests.get(url)
    return response.json()

def extract_username(url):
    # Use a regular expression to extract the username from the URL
    match = re.search(r'https://soundcloud\.com/([^/]+)', url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid SoundCloud URL format")

def display_all_entries():
    entries = get_all_entries()
    if entries:
        print("All entries in the database:")
        for entry in entries:
            print(f"User ID: {entry[0]}, Username: {entry[1]}, Permalink URL: {entry[2]}")
    else:
        print("No entries found in the database.")

def process_follower(follower, client_id, db_queue):
    follower_id = follower['id']
    if not is_user_checked(follower_id):
        follower_details = get_follower_details(follower_id, client_id)
        track_count = follower_details.get('track_count', 0)
        tracks = get_user_tracks(follower_id, client_id)

        with print_lock:
            print(f"Follower: {follower['username']} ({follower['permalink_url']}/tracks) - Tracks: {track_count}")
            for track in tracks:
                print(f"  - Track: {track['title']}")
        db_queue.put((follower_id, follower['username'], follower['permalink_url']))

def db_worker(db_queue):
    while True:
        user_id, username, permalink_url = db_queue.get()
        if user_id is None:
            break
        update_database(user_id, username, permalink_url)
        db_queue.task_done()

def main():
    client_id = 'PUT CLIENT_ID HERE'
    setup_database()

    print("Please choose an option:")
    print("1. Enter a SoundCloud URL to check followers")
    print("2. View all entries in the database")
    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        print("Please enter a SoundCloud URL in this format:")
        print("https://soundcloud.com/username")
        url = input("Enter the SoundCloud URL: ")
        username = extract_username(url)

        try:
            user_id = get_user_id(username, client_id)
            print(f"User ID for {username}: {user_id}")

            followers = get_followers(user_id, client_id)
            print(f"All followers with tracks: {len(followers)}")

            db_queue = Queue()
            db_thread = Thread(target=db_worker, args=(db_queue,))
            db_thread.start()

            with ThreadPoolExecutor(max_workers=2) as executor:
                future_to_follower = {executor.submit(process_follower, follower, client_id, db_queue): follower for follower in followers}
                for future in as_completed(future_to_follower):
                    follower = future_to_follower[future]
                    try:
                        future.result()
                    except Exception as e:
                        print(f"Error processing follower {follower['username']}: {e}")

            db_queue.join()
            db_queue.put((None, None, None))
            db_thread.join()

        except Exception as e:
            print(e)

    elif choice == '2':
        display_all_entries()

    else:
        print("Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()
