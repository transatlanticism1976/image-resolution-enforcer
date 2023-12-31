#!/usr/bin/python3

import praw
import os

from datetime import datetime
from dotenv import load_dotenv

# image width in pixels equivalent to 600DPI for standard letter paper size
MIN_IMAGE_WIDTH = 5100

LIMIT = 50


def instantiate_reddit():
    load_dotenv()
    reddit = praw.Reddit(
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        client_id=os.getenv("CLIENT_ID"),
        client_secret=os.getenv("CLIENT_SECRET"),
        user_agent="script:ImageResolutionEnforcer:v0.0.1 (by /u/{})".format(os.getenv("USERNAME")),
        ratelimit_seconds=600
    )

    print("authenticated as {}".format(reddit.user.me()))
    return(reddit)


def process_submissions(reddit) -> int:
    subreddit = reddit.subreddit("EngineeringResumes")
    num_reports = 0

    for submission in subreddit.new(limit=LIMIT):
        timestamp = datetime.fromtimestamp(int(submission.created_utc))

        if submission.link_flair_text in ("Meta", "Success Story!"):
            print(
                f"{timestamp} IGNORE {submission.author} {submission.link_flair_text}"
            )

        elif submission.link_flair_text == ("Question"):
            if any(x in submission.selftext for x in ["jpg", "jpeg", "png", "imgur"]):
                num_reports += 1
                submission.report(
                    f"potential incorrect usage of 'Question' flair. change to more appropriate flair if necessary"
                )
                print(
                    f"{timestamp} QUESTION w/ IMAGE -> REPORT {submission.author} {submission.title}"
                )
            elif submission.selftext == "":
                num_reports += 1
                submission.report(
                    f"potential incorrect usage of 'Question' flair. change to more appropriate flair if necessary"
                )
                print(f"{timestamp} QUESTION w/o BODY TEXT-> REPORT {submission.author} {submission.title}")
            else:
                print(f"{timestamp} QUESTION -> PASS {submission.author}")

        else:
            image_width = get_image_width(submission)
            dots_per_inch = round(image_width / 8.5)
            if image_width == -1:
                num_reports += 1
                submission.report(f"IMAGE MISSING")
                print(
                    f"{timestamp} IMAGE MISSING {submission.author} {submission.link_flair_text}"
                )
            elif image_width < MIN_IMAGE_WIDTH:
                num_reports += 1
                submission.report(f"LOW QUALITY IMAGE DETECTED: {dots_per_inch}DPI")
                print(
                    f"{timestamp} {dots_per_inch}DPI -> REJECT {submission.author} {submission.link_flair_text}"
                )
            else:
                print(
                    f"{timestamp} {dots_per_inch}DPI -> PASS  {submission.author} {submission.link_flair_text}"
                )
    return num_reports


def get_image_width(submission) -> int:
    s = submission.selftext
    keyword1 = "width="
    keyword2 = "&"

    if s == "" or s.find(keyword1) == -1:
        return -1
    else:
        width = s.split(keyword1)[1].split(keyword2)[0]
        return(int(width))


def main():
    reddit = instantiate_reddit()
    num_reports = process_submissions(reddit)
    print(f"number of submissions reported: {num_reports}")


if __name__ == "__main__":
    main()
