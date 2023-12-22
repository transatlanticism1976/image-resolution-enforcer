#!/usr/bin/python3

import praw
import os

from datetime import datetime
from dotenv import load_dotenv

MIN_IMAGE_WIDTH = 5100  # image width in pixels, equivalent to 600DPI for a standard letter size paper
LIMIT = 10

num_reports = 0


def instantiate_reddit():
    load_dotenv()
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    user_agent = "script:ImageResolutionEnforcer:v0.0.1 (by /u/" + username + ")"

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
    subreddit = reddit.subreddit("EngineeringResumes")
    for submission in subreddit.new(limit=LIMIT):
        global num_reports
        timestamp = datetime.fromtimestamp(int(submission.created_utc))
        if submission.link_flair_text in ("Meta", "Success Story!"):
            print(
                f"{timestamp} IGNORE {submission.author} {submission.link_flair_text}"
            )
            num_reports += 1

        elif submission.link_flair_text == ("Question"):
            if any(x in submission.selftext for x in ["jpg", "jpeg", "png", "imgur"]):
                print(
                    f"{timestamp} QUESTION w/ IMAGE {submission.author} {submission.title}"
                )
                submission.report(
                    f"potential incorrect usage of 'Question' flair. change to more appropriate flair if necessary"
                )
                num_reports += 1
            elif submission.selftext == "": # no body text
                print(f"{timestamp} QUESTION w/o BODY TEXT {submission.author} {submission.title}")
                submission.report(
                    f"potential incorrect usage of 'Question' flair. change to more appropriate flair if necessary"
                )
                num_reports += 1
            else:
                print(f"{timestamp} QUESTION PASS {submission.author}")

        else:
            image_width = get_image_width(submission)
            resolution = round(image_width / 8.5)  # convert pixels to DPI
            if image_width == 0:
                print(
                    f"{timestamp} 'width=' not found in selftext {submission.author} {submission.link_flair_text}"
                )
                submission.report(f"POST IS MISSING IMAGE")
                num_reports += 1
            elif image_width < MIN_IMAGE_WIDTH:
                print(
                    f"{timestamp} REJECT {resolution}DPI {submission.author} {submission.link_flair_text}"
                )
                num_reports += 1
                submission.report(f"LOW QUALITY IMAGE DETECTED: {resolution}DPI")
            else:
                print(
                    f"{timestamp} PASS {resolution}DPI {submission.author} {submission.link_flair_text}"
                )


def get_image_width(submission) -> int:
    s = submission.selftext  # image width is embedded into image URL '...width=5100...'
    if s == "":
        return 0
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


def main():
    reddit = instantiate_reddit()
    process_submissions(reddit)
    print(f"number of submissions reported: {num_reports}")


if __name__ == "__main__":
    main()
