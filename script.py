#!/usr/bin/python3

import praw
import time

USERNAME = "EngResBot"
PASSWORD = ""
CLIENT_ID = "Hao8ehOuXuRfjQz-kvsGxg"
CLIENT_SECRET = "-Qt2qm0skYvIZX4GCdSMxaFxhsMC0A"
USER_AGENT = "script:ImageResolutionEnforcer:v0.0.3 (by /u/EngResBot)"

MIN_WIDTH = 5100

def process_submissions(reddit):
    subreddit = reddit.subreddit('EngineeringResumes')
    for submission in subreddit.stream.submissions():
        if submission.link_flair_text in ('Question','Meta','Success Story!'):
            return
        if submission.is_self:
            width = get_width(submission) # pixels
            resolution = round(width/8.5) # convert pixels to "DPI"
            if width < MIN_WIDTH:
                print(f"REJECT {resolution}DPI {submission.author}")
                # submission.report(f"low-res image detected: {resolution}DPI")
                return
            else:
                print(f"PASS {resolution}DPI {submission.author}")
                return

# returns width of image in pixels
def get_width(submission):
    s = submission.selftext
    keyword = 'width=' # extract image width after this string in image URL
    try:
        start = s.index(keyword)
    except ValueError:
        return
    end = start + len(keyword) + 4 # extract 4 digits
    start = start + len(keyword)
    if s[end-1] == '&': # if image width is only 3 digits
        return int(s[start:(end-1)])
    else:
        return int(s[start:end])

if __name__ == "__main__":
    process_submissions(praw.Reddit(username=USERNAME, password=PASSWORD, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT))

#     for submission in subreddit.stream.submissions():
#        review_post(submission) 

# def review_post(submission):
#         if submission.link_flair_text in ('Question','Meta','Success Story!'):
#             return

#         if submission.is_self:
#             width = get_width(submission) # pixels
#             resolution = round(width/8.5) # convert pixels to "DPI"
#             if width < MIN_WIDTH:
#                 print(f"REJECT {resolution}DPI {submission.author}")
#                 # submission.report(f"low-res image detected: {resolution}DPI")
#                 return
#             else:
#                 print(f"PASS {resolution}DPI {submission.author}")
#                 return