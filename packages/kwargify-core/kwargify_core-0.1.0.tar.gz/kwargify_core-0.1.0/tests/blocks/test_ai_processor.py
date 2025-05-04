from kwargify_core.blocks.ai_processor import AIProcessorBlock
import litellm


def test_ai_processor_block_returns_response(monkeypatch):
    def mock_completion(*args, **kwargs):
        class MockChoice:
            def __init__(self):
                self.message = {"content": "This is a mocked response."}

        class MockResponse:
            def __init__(self):
                self.choices = [MockChoice()]

        return MockResponse()

    monkeypatch.setattr(litellm, "completion", mock_completion)

    block = AIProcessorBlock(config={"model": "gpt-4o-mini"})
    block.set_input("content", "What is Python?")
    block.set_input("instructions", "Give a short answer.")
    block.run()

    assert block.outputs["response"] == "This is a mocked response."
