import pytest
from unittest.mock import patch, MagicMock
from rettxmutation.analysis.openai_rettx_agents import OpenAIRettXAgents, InvalidResponse


@patch("rettxmutation.analysis.openai_rettx_agents.AzureOpenAI")
def test_extract_mutations_success(mock_azure_openai_class):
    """
    Test a successful call to extract_mutations that returns valid mutations.
    """
    # 1) Create a mock AzureOpenAI instance
    mock_azure_openai = MagicMock()
    mock_azure_openai_class.return_value = mock_azure_openai

    # 2) Mock the 'chat.completions.create' method to simulate a valid response
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(content=(
                "NM_004992.4:c.916C>T;confidence=1.0\n"
                "NM_001110792.2:c.538C>T;confidence=0.8\n"
                "Invalid;confidence=0.0"
            ))
        )
    ]
    mock_azure_openai.chat.completions.create.return_value = mock_response

    # 3) Instantiate OpenAIRettXAgents
    agent = OpenAIRettXAgents(
        api_key="fake_key",
        api_version="fake_version",
        azure_endpoint="https://fake.endpoint",
        model_name="test-model",
        audit_logger=MagicMock()
    )

    # 4) Call the method under test
    text = "This text mentions c.916C>T and c.538C>T in MECP2."
    result = agent.extract_mutations(
        audit_context="dummy-correlation-id",
        document_text=text,
        mecp2_keywords="NM_004992.4\nNM_001110792.2",
        variant_list="c.916C>T\nc.538C>T"
    )

#    # 5) Verify the result
#    assert len(result) == 2
#
#    first_mutation = result[0]
#    assert isinstance(first_mutation, GeneMutation)
#    assert first_mutation.gene_transcript == "NM_004992.4"
#    assert first_mutation.gene_variation == "c.916C>T"
#    assert first_mutation.confidence == 1.0
#
#    second_mutation = result[1]
#    assert second_mutation.gene_transcript == "NM_001110792.2"
#    assert second_mutation.gene_variation == "c.538C>T"
#    assert second_mutation.confidence == 0.8
#
#    # 6) Also ensure the mock was called correctly
#    mock_azure_openai.chat.completions.create.assert_called_once()


@patch("rettxmutation.analysis.openai_rettx_agents.AzureOpenAI")
def test_openai_fail(mock_azure_openai_class):
    """
    Test a failed call to extract_mutations that returns valid mutations.
    """
    # 1) Create a mock AzureOpenAI instance
    mock_azure_openai = MagicMock()
    mock_azure_openai_class.return_value = mock_azure_openai

    # 2) Mock the 'chat.completions.create' method to simulate a valid response
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=None))
    ]
    mock_azure_openai.chat.completions.create.return_value = mock_response

    # 3) Instantiate OpenAIRettXAgents
    agent = OpenAIRettXAgents(
        api_key="fake_key",
        api_version="fake_version",
        azure_endpoint="https://fake.endpoint",
        model_name="test-model",
        audit_logger=MagicMock()
    )

    # Must raise exception
    with pytest.raises(InvalidResponse):
        agent.extract_mutations(
            audit_context="dummy-correlation-id",
            document_text="dummy text",
            mecp2_keywords="dummy text",
            variant_list="dummy text"
        )

    # Must raise exception
    with pytest.raises(InvalidResponse):
        agent.summarize_report(
            audit_context="dummy-correlation-id",
            document_text="dummy text",
            keywords="dummy text"
        )

    # Must raise exception
    with pytest.raises(InvalidResponse):
        agent.correct_summary_mistakes(
            audit_context="dummy-correlation-id",
            document_text="dummy text",
            keywords="dummy text",
            text_analytics="dummy text"
        )


@patch("rettxmutation.analysis.openai_rettx_agents.AzureOpenAI")
def test_summarize_report_success(mock_azure_openai_class):
    """
    Test a successful call to summarize_report.
    """
    # 1) Create a mock AzureOpenAI instance
    mock_azure_openai = MagicMock()
    mock_azure_openai_class.return_value = mock_azure_openai

    # 2) Mock the 'chat.completions.create' method to simulate a valid response
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(content=(
                "This is a mock of the report summary"
            ))
        )
    ]
    mock_azure_openai.chat.completions.create.return_value = mock_response

    # 3) Instantiate OpenAIRettXAgents
    agent = OpenAIRettXAgents(
        api_key="fake_key",
        api_version="fake_version",
        azure_endpoint="https://fake.endpoint",
        model_name="test-model",
        audit_logger=MagicMock()
    )

    # 4) Call the method under test
    text = "This text mentions c.916C>T and c.538C>T in MECP2."
    result = agent.summarize_report(
        audit_context="dummy-correlation-id",
        document_text=text,
        keywords="NM_004992.4\nNM_001110792.2"
    )

    # 5) Verify the result
    assert len(result) == 36
    assert result == "This is a mock of the report summary"


@patch("rettxmutation.analysis.openai_rettx_agents.AzureOpenAI")
def test_correct_summary_mistakes_success(mock_azure_openai_class):
    """
    Test a successful call to correct_summary_mistakes.
    """
    # 1) Create a mock AzureOpenAI instance
    mock_azure_openai = MagicMock()
    mock_azure_openai_class.return_value = mock_azure_openai

    # 2) Mock the 'chat.completions.create' method to simulate a valid response
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(
            message=MagicMock(content=(
                "Mutation c.538C>T was detected in patient A"
            ))
        )
    ]
    mock_azure_openai.chat.completions.create.return_value = mock_response

    # 3) Instantiate OpenAIRettXAgents
    agent = OpenAIRettXAgents(
        api_key="fake_key",
        api_version="fake_version",
        azure_endpoint="https://fake.endpoint",
        model_name="test-model",
        audit_logger=MagicMock()
    )

    # 4) Call the method under test
    text = "Mutation c538C->T was detected in patient A"
    result = agent.correct_summary_mistakes(
        audit_context="dummy-correlation-id",
        document_text=text,
        keywords="NM_004992.4\nNM_001110792.2",
        text_analytics="c.916C>T\nc.538C>T"
    )

    # 5) Verify the result
    assert result == "Mutation c.538C>T was detected in patient A"
