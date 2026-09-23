from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

from tools import scrape_url, web_search
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# GROQ MODELS
# ============================================================

agent_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=1200
)

writer_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=1000
)

critic_llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    max_tokens=800
)


# ============================================================
# SEARCH AGENT
# ============================================================

def build_search_agent():

    return create_agent(
        model=agent_llm,
        tools=[web_search],
        system_prompt=(
            "You are a professional web research agent. "
            "Use the web_search tool to find recent, reliable "
            "and relevant information. "
            "Return concise findings and relevant URLs."
        ),
        name="search_agent"
    )


# ============================================================
# READER AGENT
# ============================================================

def build_reader_agent():

    return create_agent(
        model=agent_llm,
        tools=[scrape_url],
        system_prompt=(
            "You are a professional research reader. "
            "Select the most relevant URL from the search results "
            "and use scrape_url to read it. "
            "Return only the important facts relevant to the topic."
        ),
        name="reader_agent"
    )


# ============================================================
# WRITER CHAIN
# ============================================================

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert research writer.

Write a clear, factual and professional research report.
Keep the response concise.
"""
    ),
    (
        "human",
        """
Topic:
{topic}

Research:
{research}

Write:

1. Introduction
2. Key Findings
3. Conclusion
4. Sources

Do not unnecessarily repeat information.
"""
    )
])

writer_chain = writer_prompt | writer_llm | StrOutputParser()


# ============================================================
# CRITIC CHAIN
# ============================================================

critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert research critic.

Review the report for factual clarity,
completeness, logical consistency and source usage.

Keep your response concise.
"""
    ),
    (
        "human",
        """
Review this report:

{report}

Give:

1. Strengths
2. Problems
3. Improvements
"""
    )
])

critic_chain = critic_prompt | critic_llm | StrOutputParser()