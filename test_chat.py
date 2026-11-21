from types import SimpleNamespace
from unittest.mock import MagicMock

import anthropic
import httpx2
import pytest

import chat

REQUEST = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")


def make_response(text):
    return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)])


def scripted_input(*lines, end=EOFError):
    """Return an input() replacement that yields lines, then raises end."""
    remaining = list(lines)

    def fake_input(prompt=""):
        if remaining:
            return remaining.pop(0)
        raise end

    return fake_input


@pytest.fixture
def client():
    return MagicMock()


def test_empty_and_whitespace_input_is_skipped(client):
    history = chat.run_chat(client, scripted_input("", "   ", "\t\n", "exit"))

    client.messages.create.assert_not_called()
    assert history == []


@pytest.mark.parametrize(
    "error",
    [
        anthropic.APIConnectionError(request=REQUEST),
        anthropic.InternalServerError(
            "Internal server error",
            response=httpx2.Response(500, request=REQUEST),
            body=None,
        ),
    ],
    ids=["connection", "server"],
)
def test_api_error_does_not_crash_or_corrupt_history(client, capsys, error):
    client.messages.create.side_effect = [error, make_response("Hi there!")]

    history = chat.run_chat(client, scripted_input("hello", "try again", "exit"))

    assert "Error:" in capsys.readouterr().out
    # The failed "hello" is gone; the conversation continues cleanly.
    assert history == [
        {"role": "user", "content": "try again"},
        {"role": "assistant", "content": "Hi there!"},
    ]


def test_normal_reply_is_appended(client, capsys):
    client.messages.create.return_value = make_response("Paris.")

    history = chat.run_chat(client, scripted_input("  Capital of France?  ", "exit"))

    assert history == [
        {"role": "user", "content": "Capital of France?"},
        {"role": "assistant", "content": "Paris."},
    ]
    assert "Claude: Paris." in capsys.readouterr().out


def test_reply_skips_non_text_blocks(client):
    client.messages.create.return_value = SimpleNamespace(
        content=[
            SimpleNamespace(type="thinking", thinking=""),
            SimpleNamespace(type="text", text="Answer"),
        ]
    )

    history = chat.run_chat(client, scripted_input("question", "exit"))

    assert history[-1] == {"role": "assistant", "content": "Answer"}


@pytest.mark.parametrize("end", [KeyboardInterrupt, EOFError], ids=["ctrl-c", "ctrl-d"])
def test_ctrl_c_and_ctrl_d_exit_cleanly(client, capsys, end):
    history = chat.run_chat(client, scripted_input(end=end))

    assert history == []
    assert "Goodbye!" in capsys.readouterr().out


def test_ctrl_c_during_request_exits_without_dangling_message(client, capsys):
    client.messages.create.side_effect = KeyboardInterrupt

    history = chat.run_chat(client, scripted_input("hello"))

    assert history == []
    assert "Goodbye!" in capsys.readouterr().out
