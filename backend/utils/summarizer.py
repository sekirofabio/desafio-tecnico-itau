from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from utils.prompt import SYSTEM_PROMPT

async def text_summarizer(original_text: str, word_count: int) -> str:
    """
    Summarize a text into a given number of words using LangChain LCEL.
    """

    llm = ChatOpenAI(
        model="gpt-5.1",
        temperature=0
    )

    prompt = PromptTemplate(
        template=SYSTEM_PROMPT,
        input_variables=["original_text", "word_count"]
    )

    chain = prompt | llm

    response = await chain.ainvoke({
        "original_text": original_text,
        "word_count": word_count
    })

    return response.content
