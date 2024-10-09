import tweepy
import pandas as pd
import time
import os  # For handling file paths

# Enter API tokens below
bearer_token = 'AAAAAAAAAAAAAAAAAAAAAJYdwQEAAAAANxqWHFpvPmdP3R5hGToVZcI%2FA7Q%3Daq0MiDngp74ZUlspMjEI6sNy53lbrHa3loE9YuNVXtPu15tVlU'
consumer_key = 'pUpVGy2DWTKoakjNi3tZZHbt4'
consumer_secret = 'SiWdIlct35zDhlFWtnaEHj0z99nGXwo6iwRstTTtPSCgwgrJiQ'
access_token = '1803410091728916480-7PplouBKbNFVE5ZxcF2sjTMhTW0vVS'
access_token_secret = 'b07DHtcflCoXfW9l2mv2xLMsfWEBFAmwdzdPngaJt5VMq'

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
df = pd.read_csv('tweets_day5.csv')

# Iterate through the rows in the DataFrame and post tweets
for index, row in df.iterrows():
    text = row['text']
    image_path = row['image']

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

    # Wait for 5 minutes before posting the next tweet
    if index < len(df) - 1:  # To avoid waiting after the last tweet
        print("Waiting for 5 minutes before posting the next tweet...")
        time.sleep(300)  # 5 minutes in seconds
