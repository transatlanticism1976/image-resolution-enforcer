#!/usr/bin/python3

import praw
from datetime import datetime

USERNAME = ""
PASSWORD = ""
CLIENT_ID = ""
CLIENT_SECRET = ""
USER_AGENT = "script:ImageResolutionEnforcer:v0.0.1 (by /u/)"

MIN_WIDTH = 5100 # width in pixels. equivalent to 600DPI for a standard letter size paper

def process_submissions(reddit):
    subreddit = reddit.subreddit('EngineeringResumes')
    for submission in subreddit.new(limit=25):
        timestamp = datetime.utcfromtimestamp(int(submission.created_utc))
        if submission.link_flair_text in ('Question','Meta','Success Story!'):
            print(f"{timestamp} {submission.link_flair_text} {submission.author}")
            continue   
        if submission.is_self:  
            width = get_width(submission)
            if width == 0:
                print(f"{timestamp} INVALID {submission.author} {submission.link_flair_text}")
                continue
            resolution = round(width/8.5) # convert to DPI
            if width < MIN_WIDTH:
                print(f"{timestamp} REJECT {resolution}DPI {submission.author} {submission.link_flair_text}")
                # reddit.redditor("").message(subject="blurry image alert", message=f"{submission.permalink} {submission.link_flair_text} {resolution}DPI")
                # submission.report(f"low-res image detected: {resolution}DPI")
                return
            else:
                print(f"{timestamp} PASS {submission.link_flair_text} {submission.author}")
                return


def get_width(submission):
    s = submission.selftext
    keyword = 'width=' # keyword found in image URL: '...width=5100...'
    try:
        start = s.index(keyword)
    except ValueError: # keyword not found
        return 0
    start = start + len(keyword)
    end = start + 4 # extract 4 digits
    if s[end-1] == '&': # if width is only 3 digits
        return int(s[start:(end-1)])
    else:
        return int(s[start:end])

if __name__ == "__main__":
    process_submissions(praw.Reddit(
        username=USERNAME, 
        password=PASSWORD, 
        client_id=CLIENT_ID, 
        client_secret=CLIENT_SECRET, 
        user_agent=USER_AGENT
    ))
