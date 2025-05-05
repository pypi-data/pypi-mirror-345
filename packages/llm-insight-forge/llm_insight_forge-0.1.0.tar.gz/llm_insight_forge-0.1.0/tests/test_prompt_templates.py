"""
Tests for the prompt template system.
"""
import pytest
from llm_insight_forge.prompt_engineering.template import (
    PromptTemplate,
    ChatPromptTemplate,
    SystemMessageTemplate,
    UserMessageTemplate,
    AssistantMessageTemplate,
    FewShotTemplate,
    Example,
    TemplateError
)


class TestPromptTemplate:
    def test_basic_template(self):
        template = PromptTemplate("Answer the following question about {topic}: {question}")
        rendered = template.render(topic="astronomy", question="How big is the sun?")
        expected = "Answer the following question about astronomy: How big is the sun?"
        assert rendered == expected
    
    def test_missing_variable(self):
        template = PromptTemplate("Answer the following question about {topic}: {question}")
        with pytest.raises(TemplateError):
            template.render(topic="astronomy")  # Missing question variable
    
    def test_extra_variable(self):
        template = PromptTemplate("Answer the following question about {topic}: {question}")
        rendered = template.render(topic="astronomy", question="How big is the sun?", extra="ignored")
        expected = "Answer the following question about astronomy: How big is the sun?"
        assert rendered == expected
    
    def test_conditional_blocks(self):
        template = PromptTemplate(
            "Answer the following question about {topic}: {question}"
            "{% if extra_info %}Additional context: {extra_info}{% endif %}"
        )
        # With extra_info
        rendered = template.render(
            topic="astronomy", 
            question="How big is the sun?", 
            extra_info="The sun is a G-type main-sequence star."
        )
        expected = "Answer the following question about astronomy: How big is the sun?Additional context: The sun is a G-type main-sequence star."
        assert rendered == expected
        
        # Without extra_info
        rendered = template.render(topic="astronomy", question="How big is the sun?", extra_info="")
        expected = "Answer the following question about astronomy: How big is the sun?"
        assert rendered == expected
    
    def test_to_dict_from_dict(self):
        original = PromptTemplate(
            "Answer the following question about {topic}: {question}",
            template_type="text",
            metadata={"author": "test"}
        )
        data = original.to_dict()
        restored = PromptTemplate.from_dict(data)
        
        assert restored.template == original.template
        assert restored.template_type == original.template_type
        assert restored.variables == original.variables
        assert restored.metadata == original.metadata


class TestChatPromptTemplate:
    def test_basic_chat_template(self):
        template = ChatPromptTemplate(
            messages=[
                SystemMessageTemplate("You are a helpful assistant specialized in {domain}."),
                UserMessageTemplate("Explain {concept} in simple terms.")
            ]
        )
        
        rendered = template.render(domain="astronomy", concept="black holes")
        
        assert len(rendered) == 2
        assert rendered[0]["role"] == "system"
        assert rendered[0]["content"] == "You are a helpful assistant specialized in astronomy."
        assert rendered[1]["role"] == "user"
        assert rendered[1]["content"] == "Explain black holes in simple terms."
    
    def test_variable_extraction(self):
        template = ChatPromptTemplate(
            messages=[
                SystemMessageTemplate("You are a helpful assistant specialized in {domain}."),
                UserMessageTemplate("Explain {concept} in simple terms.")
            ]
        )
        
        assert sorted(template.variables) == sorted(["domain", "concept"])
    
    def test_to_dict_from_dict(self):
        original = ChatPromptTemplate(
            messages=[
                SystemMessageTemplate("You are a helpful assistant specialized in {domain}."),
                UserMessageTemplate("Explain {concept} in simple terms.")
            ],
            metadata={"author": "test"}
        )
        
        data = original.to_dict()
        restored = ChatPromptTemplate.from_dict(data)
        
        assert len(restored.messages) == len(original.messages)
        assert restored.messages[0].role == original.messages[0].role
        assert restored.messages[0].content == original.messages[0].content
        assert restored.messages[1].role == original.messages[1].role
        assert restored.messages[1].content == original.messages[1].content
        assert restored.metadata == original.metadata


class TestFewShotTemplate:
    def test_few_shot_template(self):
        template = FewShotTemplate(
            template="I need you to classify the sentiment of texts as positive or negative.\n\n{examples}\n\nText: {input}\nSentiment:",
            examples=[
                Example(
                    input="I love this product!", 
                    output="Positive"
                ),
                Example(
                    input="This is terrible, don't buy it.", 
                    output="Negative"
                )
            ],
        )
        
        rendered = template.render(input="The service was okay.")
        
        assert "I need you to classify the sentiment" in rendered
        assert "I love this product!" in rendered
        assert "Positive" in rendered
        assert "This is terrible" in rendered
        assert "Negative" in rendered
        assert "The service was okay" in rendered
    
    def test_custom_example_format(self):
        template = FewShotTemplate(
            template="Answer the following questions based on the examples:\n\n{examples}\n\nQuestion: {question}\nAnswer:",
            examples=[
                Example(
                    input="What is the capital of France?", 
                    output="Paris"
                ),
                Example(
                    input="What is the capital of Japan?", 
                    output="Tokyo"
                )
            ],
            example_format="Q: {input}\nA: {output}"
        )
        
        rendered = template.render(question="What is the capital of Italy?")
        
        assert "Q: What is the capital of France?" in rendered
        assert "A: Paris" in rendered
        assert "Q: What is the capital of Japan?" in rendered
        assert "A: Tokyo" in rendered
        assert "Question: What is the capital of Italy?" in rendered