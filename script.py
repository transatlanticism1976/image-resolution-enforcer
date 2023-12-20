#!/usr/bin/python3

import praw
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_AGENT = "script:ImageResolutionEnforcer:v0.0.1 (by /u/transatlanticism1976)"
MIN_WIDTH = 5100  # image width in pixels. equivalent to 600DPI for a standard letter size paper

counter = 0


def main():
    print("authenticating..")
    reddit = praw.Reddit(
        username=USERNAME,
        password=PASSWORD,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT,
    )
    print("authenticated as {}".format(reddit.user.me()))
    process_submissions(reddit)
    print("completed processing submissions")
    print(f"total number of submissions processed: {counter}")


def process_submissions(reddit):
    print("processing submissions...")
    subreddit = reddit.subreddit("EngineeringResumes")
    for submission in subreddit.new(limit=25):
        global counter
        counter += 1
        timestamp = datetime.fromtimestamp(int(submission.created_utc))
        if submission.link_flair_text in ("Question", "Meta", "Success Story!"):
            print(
                f"{timestamp} {resolution}DPI {submission.author} {submission.link_flair_text}"
            )
            continue
        if submission.is_self:
            width = get_image_width(submission)
            if width == 0:
                print(
                    f"{timestamp} INVALID {submission.author} {submission.link_flair_text}"
                )
                continue
            resolution = round(width / 8.5)  # convert pixels to DPI
            if width < MIN_WIDTH:
                print(
                    f"{timestamp} FAIL {resolution}DPI {submission.author} {submission.link_flair_text}"
                )
                reddit.redditor(USERNAME).message(
                    subject=f"blurry image alert: resolution: {resolution}DPI",
                    message=f"{submission.permalink} flair: {submission.link_flair_text} by /u/{submission.author}",
                )
                submission.report(f"low-res image detected: {resolution}DPI")
                return
            else:
                print(
                    f"{timestamp} PASS {resolution}DPI {submission.author} {submission.link_flair_text}"
                )
                return


def get_image_width(submission):
    s = submission.selftext  # PNG width is embedded into image URL '...width=5100...'
    keyword = "width="
    try:
        start = s.index(keyword)
    except ValueError:  # user did not follow submission instructions
        return 0
    start = start + len(keyword)
    end = start + 4  # extract 4 digits
    if s[end - 1] == "&":  # if width is only 3 digits
        return int(s[start : (end - 1)])
    else:
        return int(s[start:end])


if __name__ == "__main__":
    main()
