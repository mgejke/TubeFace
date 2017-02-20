import facebook
import requests

import re
import os

from urllib import parse
from datetime import datetime
from dateutil import tz

import webbrowser
import youtube

###################################

# Enter your facebook app details here:
fb_client_id = ''
fb_secret = ''

# Enter the group id as a string
group_id = ''

# A list of message ids(as strings) in the group to skip
skipped_ids = []

# Base name of generated playlist, dates will be added
playlist_base = ''

###################################

youtube_re = re.compile('^(https?\:\/\/)?((www\.)?youtube\.com|youtu\.?be)\/.+$')
id_re = re.compile('.*(\?v=|ci=|.be\/)(.{11})')

already_posted_file = 'already_posted.txt'

dry_run = True
max_past = 31


def parse_time(time):
    date = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S%z')
    return date.astimezone(tz.tzlocal())


def get_from_post(post, video_list):
    message = []
    
    date = parse_time(post['created_time'])

    if 'message' in post:
        message.extend(post['message'].split(' '))

    if 'link' in post and post['link'] not in message:
        message.append(post['link'])

    if len(message) > 0:
        video_list.append((message, date))

    return date

def token_fail():
    print('Save token in token.txt')
    webbrowser.open_new_tab('https://developers.facebook.com/tools/explorer/')


def get_graph(token):
    graph = facebook.GraphAPI(token, version='2.7')

    print('Refreshing token...')
    try:
        result = graph.extend_access_token(fb_client_id, fb_secret)
    except facebook.GraphAPIError as e:
        token_fail()
        return None
    else:
        token = result['access_token']
        graph.access_token = token
        with open('token.txt', 'w') as f:
            f.write(token)
        return graph


def get_video_candidates(graph, group_id):
    res = graph.get_object(group_id, 
        fields='feed.limit(20){message, created_time, link, from, comments.limit(20)}')
    feed = res['feed']

    today = datetime.today().replace(tzinfo=tz.tzlocal())
    found_older = False
    videos = []

    while not found_older:
        for post in feed['data']:

            if post['id'] in skipped_ids:
                print('*'*5, 'Skipping post...', '*'*5)
                continue

            date = parse_time(post['created_time'])
            if (today - date).days > max_past:
                found_older = True
                break

            date = get_from_post(post, videos)
            print('Post by {} - {}'.format(post['from']['name'], date))

            if 'comments' in post:
                for comment in post['comments']['data']:
                    date = get_from_post(comment, videos)
                    print('\tComment by {} - {}'.format(comment['from']['name'], date))

            print()

        if 'paging' in feed:
            feed = requests.get(feed['paging']['next']).json()
        else:
            break

    return videos

def extract_ids(videos):
    
    already_posted = []
    if os.path.exists(already_posted_file):

        with open(already_posted_file, 'r') as f:

            already_posted = [line.rstrip('\n') for line in f]
    
    dates = []
    with open(already_posted_file, 'a') as f:


        ids = []    
        for message, date in videos:
            for word in message:
                if not youtube_re.search(word):
                    continue

                unqouted = parse.unquote(word)
                match = id_re.match(unqouted)

                if not match:
                    continue

                try:
                    id_ = match.group(2)
                except IndexError as e:
                    print(e, unqouted)
                    continue

                if id_ in already_posted:
                    continue

                print(date, id_, unqouted)

                ids.append(id_)
                dates.append(date)
                if not dry_run:
                    f.write('{}\n'.format(id_))

    return dates, ids


def main():
    token = None
    
    try:
        with open('token.txt') as f:
            token = f.read()
    except Exception as e:
        print(str(e))
        token_fail()
        return
    
    graph = get_graph(token)
    if not graph:
        return

    videos = get_video_candidates(graph, group_id)
    dates, ids = extract_ids(videos)

    print('\nFound {} new videos\n'.format(len(ids)))
    if len(ids) == 0:
        return

    dates.sort()
    from_date = dates[0].strftime("%y-%m-%d")
    to_date = dates[-1].strftime("%y-%m-%d")

    playlist_name = '{} {} - {}'.format(playlist_base, from_date, to_date)
    print(playlist_name)
    
    if not dry_run:
        playlist_id = youtube.create_playlist(playlist_name, '')
        for video_id in ids:
            youtube.add_video_to_playlist(video_id, playlist_id)
        

if __name__ == '__main__':
    main()