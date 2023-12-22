#!/usr/bin/python3

import praw
import os
import time
from datetime import datetime
from dotenv import load_dotenv

MIN_WIDTH = 5100  # image width in pixels, equivalent to 600DPI for a standard letter size paper
LIMIT = 50
counter = 0


def main():
    start_time = time.time()

    reddit = instantiate_reddit()

    process_submissions(reddit)

    print("completed processing submissions")
    print(f"total number of submissions processed: {counter}")
    print("program took", time.time() - start_time, "seconds to run")


def instantiate_reddit():
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    user_agent = "script:ImageResolutionEnforcer:v0.0.1 (by /u/" + username + ")"

    print("authenticating..")
    reddit = praw.Reddit(
        username=username,
        password=password,
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
        ratelimit_seconds=600
    )

    print("authenticated as {}".format(reddit.user.me()))
    return(reddit)


def process_submissions(reddit):
    print("processing submissions...")
    subreddit = reddit.subreddit("EngineeringResumes")
    for submission in subreddit.new(limit=LIMIT):
        global counter
        counter += 1
        timestamp = datetime.fromtimestamp(int(submission.created_utc))
        if submission.link_flair_text in ("Meta", "Success Story!"):
            print(
                f"{timestamp} IGNORE {submission.author} {submission.link_flair_text}"
            )

        elif submission.link_flair_text == ("Question"):
            if any(x in submission.selftext for x in ["jpg", "jpeg", "png", "imgur"]):
                print(
                    f"{timestamp} QUESTION: IMAGE DETECTED {submission.author}"
                )
                submission.report(
                    f"potential incorrect usage of 'Question' flair. change to more appropriate flair if necessary"
                )
            elif submission.selftext == "": # no body text
                print(f"{timestamp} QUESTION: NO BODY TEXT {submission.author}")
                submission.report(
                    f"potential incorrect usage of 'Question' flair. change to more appropriate flair if necessary"
                )
            else:
                print(f"{timestamp} QUESTION: NO BODY TEXT {submission.author}")

        else:
            width = get_image_width(submission)
            if width == 0:
                print(
                    f"{timestamp} INVALID {submission.author} {submission.link_flair_text}"
                )
            resolution = round(width / 8.5)  # convert pixels to DPI
            if width < MIN_WIDTH:
                print(
                    f"{timestamp} FAIL {resolution}DPI {submission.author} {submission.link_flair_text}"
                )
                submission.report(f"LOW QUALITY IMAGE DETECTED: {resolution}DPI")
            else:
                print(
                    f"{timestamp} PASS {resolution}DPI {submission.author} {submission.link_flair_text}"
                )


def get_image_width(submission):
    s = submission.selftext  # image width is embedded into image URL '...width=5100...'
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
