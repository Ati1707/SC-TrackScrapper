import requests
import time
import re

from user_database import *


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
            print(f"Failed to get followers: {response.status_code}. Retrying...")
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

            for follower in followers:
                follower_id = follower['id']
                if not is_user_checked(follower_id):
                    follower_details = get_follower_details(follower_id, client_id)
                    track_count = follower_details.get('track_count', 0)
                    print(f"Follower: {follower['username']} ({follower['permalink_url']}) - Tracks: {track_count}")
                    update_database(follower_id, follower['username'], follower['permalink_url'])
                else:
                    print(f"Follower {follower['username']} already in database.")

        except Exception as e:
            print(e)

    elif choice == '2':
        display_all_entries()

    else:
        print("Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()
