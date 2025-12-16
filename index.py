import base64
import requests
import boto3
import json

ACCESS_KEY = "AKIAZGNHKJJ44SLJZQ5D///"
ACCESS_SECRET = "qLFNrNK3xTuu8OtHkEtho/kj1RsUWD/L41/F57Xa//"
BUCKET_NAME = "spotify1-bucket"
REGION_NAME = "ap-south-1"
OBJECT_NAME = "spotify/spotifydata.json"

# Create S3 client
s3_client = boto3.client(
    service_name="s3",
    region_name=REGION_NAME,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=ACCESS_SECRET
)

# Spotify credentials
CLIENT_ID = "51bd4158c26341d8a2929beb2c872314"
CLIENT_SECRET = "6cace97e5c674cc89de91fc8e6e79c71"

# creating a token for spotify
def access_token():
    try:
        credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {encoded_credentials}"},
            data={"grant_type": "client_credentials"}
        )
        print("Token Generated Successfully.....")
        return response.json()["access_token"]
    except Exception as e:
        print("Error in Token Generation....", e)

# Latest release in spotify
def get_new_release():
    try:
        token = access_token()
        header = {"Authorization": f"Bearer {token}"}
        Param = {"limit": 50}

        response = requests.get(
            "https://api.spotify.com/v1/browse/new-releases",
            headers=header,
            params=Param
        )

        if response.status_code == 200:
            data = response.json()
            albums = data["albums"]["items"]

            spotify_list = []   #  NEW: store data here

            for album in albums:
                info = {
                    "album_name": album["name"],
                    "artists_name": album["artists"][0]["name"],
                    "release_date": album["release_date"],
                    "album_type": album["album_type"],
                    "total_tracks": album["total_tracks"],
                    "spotify_url": album["external_urls"]["spotify"],
                    "album_image": album["images"][0]["url"] if album["images"] else None
                }
                spotify_list.append(info)

            # Upload JSON directly to S3
            s3_client.put_object(
                Bucket=BUCKET_NAME,
                Key=OBJECT_NAME,
                Body=json.dumps(spotify_list, indent=2),
                ContentType="application/json"
            )

            print(" Spotify JSON uploaded successfully to S3")

    except Exception as e:
        print("error in latest data fetching.....", e)

get_new_release()
