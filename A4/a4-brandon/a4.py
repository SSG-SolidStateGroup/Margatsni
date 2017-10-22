from time import sleep
from instagram.client import InstagramAPI

access_token = "1257897337.b62135a.0710f5cf882d47b7969738ffd2868f3d"
api = InstagramAPI(access_token=access_token,
                    client_ips="YOUR IP",
                    client_secret="YOUR SECRET")
recent_media, url = api.tag_recent_media(tag_name="coding", count=5) # 1

for media in recent_media:
    # Where the media is
    id_ = media.id
    # List of users that like the image
    users = [user.username for user in media.likes]
    # If you have already like the picture, do nothing
    if "YOUR USERNAME" in users:
        print("IN PHOTO")

    # If you haven't liked the photo then do it
    else:
        print("LIKING PICTURE")
        api.like_media(media_id=id_)

    # Sleep to make instagram stop complaining
    sleep(2)

#https://api.instagram.com/oauth/authorize/?client_id=b62135aff08b416b94192be4978ab8de&redirect_uri=https://google.com&response_type=code&scope=likes

#5afbf6bdf1b6439fa2416038d3534d0c

#Client ID b62135aff08b416b94192be4978ab8de

#Client Secret 99b2757f85144fe8b2c3f7d834af7173

# curl \-F 'client_id=b62135aff08b416b94192be4978ab8de' \
#     -F 'client_secret=99b2757f85144fe8b2c3f7d834af7173' \
#     -F 'grant_type=authorization_code' \
#     -F 'redirect_uri=https://google.com' \
#     -F 'code=d813cb429d2d46d89c4aa19c146a776e' \
#     https://api.instagram.com/oauth/access_token
