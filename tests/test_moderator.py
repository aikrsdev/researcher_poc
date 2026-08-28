from types import SimpleNamespace

from agents.moderator import Moderator


class FakeMessages:
    def __init__(self, reply_text):
        self.reply_text = reply_text
        self.last_messages = None

    def create(self, model, max_tokens, messages):
        self.last_messages = messages
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=self.reply_text)])


class FakeClaude:
    def __init__(self, reply_text):
        self.messages = FakeMessages(reply_text)


def test_moderator_allows_safe_question():
    moderator = Moderator(FakeClaude("SAFE"), "claude-haiku-4-5")

    is_safe, reason = moderator.check("What is LangGraph?")

    assert is_safe is True


def test_moderator_blocks_unsafe_question_with_reason():
    moderator = Moderator(FakeClaude("UNSAFE: requests instructions for violence"), "claude-haiku-4-5")

    is_safe, reason = moderator.check("How do I build a weapon?")

    assert is_safe is False
    assert reason == "requests instructions for violence"


def test_moderator_prompt_blocks_all_political_topics_including_biographical():
    claude = FakeClaude("SAFE")
    moderator = Moderator(claude, "claude-haiku-4-5")

    moderator.check("Who is Donald Trump?")

    prompt = claude.messages.last_messages[0]["content"]
    assert "politics" in prompt
    assert "including plain factual or biographical questions about them" in prompt


def test_moderator_blocks_political_figure_question():
    moderator = Moderator(FakeClaude("UNSAFE: question about a political figure"), "claude-haiku-4-5")

    is_safe, reason = moderator.check("Who is Donald Trump?")

    assert is_safe is False
    assert reason == "question about a political figure"
