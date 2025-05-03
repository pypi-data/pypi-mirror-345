import sys

from pygeai.cli.commands import Command, Option, ArgumentsEnum
from pygeai.cli.commands.builders import build_help_text
from pygeai.cli.texts.help import FEEDBACK_HELP_TEXT
from pygeai.core.common.exceptions import MissingRequirementException, WrongArgumentError
from pygeai.core.feedback.clients import FeedbackClient


def show_help():
    """
    Displays help text in stdout
    """
    help_text = build_help_text(feedback_commands, FEEDBACK_HELP_TEXT)
    sys.stdout.write(help_text)


def send_feedback(option_list: list):
    request_id = None
    origin = "user-feedback"
    answer_score = None
    comments = None

    for option_flag, option_arg in option_list:
        if option_flag.name == "request_id":
            request_id = option_arg
        if option_flag.name == "origin":
            origin = option_arg
        if option_flag.name == "answer_score":
            answer_score = option_arg
        if option_flag.name == "comments":
            comments = option_arg

    if not (request_id and answer_score and answer_score):
        raise MissingRequirementException("Cannot send feedback without specifying request_id and answer_score")

    client = FeedbackClient()
    result = client.send_feedback(
        request_id=request_id,
        origin=origin,
        answer_score=answer_score,
        comments=comments
    )
    sys.stdout.write(f"Feedback detail: \n{result}\n")


send_feedback_options = [
    Option(
        "request_id",
        ["--request-id", "--rid"],
        "The request associated with a user's execution. Integer",
        True
    ),
    Option(
        "origin",
        ["--origin"],
        "Origin for the feedback. Defaults to user-feedback",
        True
    ),
    Option(
        "answer_score",
        ["--answer-score", "--ans-score", "--score"],
        "Associated feedback: 1 good, 2 bad",
        True
    ),
    Option(
        "comments",
        ["--comments"],
        "Associated feedback comment (optional)",
        True
    )
]


feedback_commands = [
    Command(
        "help",
        ["help", "h"],
        "Display help text",
        show_help,
        ArgumentsEnum.NOT_AVAILABLE,
        [],
        []
    ),
    Command(
        "send_feedback",
        ["send", "sf"],
        "Send feedback",
        send_feedback,
        ArgumentsEnum.REQUIRED,
        [],
        send_feedback_options
    ),
]
