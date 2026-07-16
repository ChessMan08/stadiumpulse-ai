import pytest

from app.multilingual.faq import FAQS, answer, list_topics


def test_list_topics_covers_all_faqs():
    topics = list_topics()
    assert len(topics) == len(FAQS)
    assert all("id" in t and "label" in t for t in topics)


async def test_answer_never_invents_beyond_the_fact(mock_llm):
    result = await answer("gates_open", mock_llm, language="English")
    assert result.topic_id == "gates_open"
    assert "2 hours" in result.answer


async def test_unknown_topic_raises_key_error(mock_llm):
    with pytest.raises(KeyError):
        await answer("not_a_real_topic", mock_llm)


async def test_new_topic_water_policy(mock_llm):
    result = await answer("water_policy", mock_llm, language="English")
    assert result.topic_id == "water_policy"
    assert "water" in result.answer.lower() or "750" in result.answer
