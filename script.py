#!/usr/bin/python3

import praw

USERNAME = ""
PASSWORD = ""
CLIENT_ID = ""
CLIENT_SECRET = ""
USER_AGENT = "script:ImageResolutionEnforcer:v0.0.1 (by /u/)"

MIN_WIDTH = 5100 # pixels. equivalent to 600DPI for a standard letter size paper

def process_submissions(reddit):
    subreddit = reddit.subreddit('EngineeringResumes')
    for submission in subreddit.new(limit=10):
        if submission.link_flair_text in ('Question','Meta','Success Story!'):
            continue # skip submission 
        if submission.is_self:
            width = get_width(submission)
            resolution = round(width/8.5) # convert to DPI
            if width < MIN_WIDTH:
                print(f"{submission.created_utc} REJECT {resolution}DPI {submission.author}")
                # submission.report(f"low-res image detected: {resolution}DPI")
                return
            else:
                print(f"{submission.created_utc} PASS {resolution}DPI {submission.author}")
                return

def get_width(submission):
    print('D')
    s = submission.selftext
    keyword = 'width=' # extract image width after this string in image URL
    try:
        start = s.index(keyword)
    except ValueError:
        # print(ValueError) # TODO test
        return
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
