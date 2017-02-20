Simple script to find youtube videos in a facebook group and create youtube-playlists. 

Steps before use
================

  1. Clone this repo
  2. Setup python env
    * Create virtual env(optional)
    * ```pip install -r requirements.txt```
  3. Create youtube app
    * https://console.cloud.google.com/
    * Enable youtube api for your app
    * Generate client_secrets.json file and save it in cloned folder
  4. Create facebook app
    * Add fb_client_id and fb_secret to main.py
    * Go to https://developers.facebook.com/tools/explorer/ and choose your generated app, click Get Token -> Get User Access Token and add user_managed_groups permission
    * Copy and paste the generated access token and save it in token.txt in cloned folder
  5. Find out your groups id (hint, it's in the url) and add it to main.py
  6. Choose a great base name for your playlists and add it to main.py
  7. ???
  
Other
=====

As a default the script only checks 31 days back in time. 
Playlist are generated as private. 
Already posted video ids are stored in a local file. 
    
    
    
