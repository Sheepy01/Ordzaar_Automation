import tweepy
import pandas as pd
import time
import os
import random

# Enter API tokens below
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAGj8wgEAAAAAlbp6xgpNHH2JsLiQabfZvLFlf1g%3DNVN5iR7fZRpzP7Awx5EXxN6bdlkMs0huOZyZyrsoTyRkYc4RxI'
consumer_key = '5cJO9UGRY4tGcVXO30LmRTMLR'
consumer_secret = 'dsmTZ0YfazYPXDgmj4BV3rfD4FUXfK13ACpfRsLvgAwgTbajt8'
access_token = '1803410091728916480-qf1cP19HtKfDPBRP0o7damrQxy9cOK'
access_token_secret = 'Ckb9kc35EM6dsmVd2vdjpZVKYgOLK4RmqB66QaW5IJmQL'

# V1 Twitter API Authentication
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# V2 Twitter API Authentication
client = tweepy.Client(
    bearer_token,
    consumer_key,
    consumer_secret,
    access_token,
    access_token_secret,
    wait_on_rate_limit=True,
)

# Load the CSV file with tweets and image paths
df = pd.read_csv('all_tweets.csv')

# Directory containing images to choose from if no image is specified
image_directory = "C:/Users/micro/OneDrive/Desktop/Projects/Scripts/Ordzaar_Automation/images/"

# Helper function to pick a random image if no image is specified
def pick_random_image(directory):
    images = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    if images:
        return os.path.join(directory, random.choice(images))
    else:
        raise FileNotFoundError("No images found in the specified directory.")

# Iterate through the rows in the DataFrame and post tweets
for index, row in df.iterrows():
    text = row['text']
    image_path = row['image'] if pd.notna(row['image']) else pick_random_image(image_directory)

    # Ensure image extension is correct by checking if the file exists
    if not os.path.isfile(image_path):
        # Check different extensions (.jpg, .jpeg, .png)
        for ext in ['.jpg', '.jpeg', '.png']:
            new_image_path = os.path.splitext(image_path)[0] + ext
            if os.path.isfile(new_image_path):
                image_path = new_image_path
                break
        else:
            print(f"Image not found: {image_path}")
            continue  # Skip to the next row if no valid image is found

    # Upload the image to Twitter with retry logic
    for attempt in range(3):  # Try up to 3 times
        try:
            media_id = api.media_upload(filename=image_path).media_id_string
            print(f"Uploaded image {image_path}: media_id = {media_id}")

            # Post the tweet with text and image
            client.create_tweet(text=text, media_ids=[media_id])
            print(f"Tweeted: {text}")
            break  # Break the loop if successful

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: Error uploading {image_path} or tweeting: {e}")
            if attempt == 2:  # If last attempt fails, give up
                print("Failed to upload after 3 attempts.")
        
        time.sleep(5)  # Wait a bit before retrying (5 seconds)

    # Wait for a random time between 30 seconds and 2 minutes before posting the next tweet
    if index < len(df) - 1:  # To avoid waiting after the last tweet
        wait_time = random.randint(20, 35)  # Random wait time between 30 seconds and 2 minutes
        print(f"Waiting for {wait_time} seconds before posting the next tweet...")
        time.sleep(wait_time)
