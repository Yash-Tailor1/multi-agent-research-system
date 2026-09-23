from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser

from tools import scrape_url, web_search
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# GROQ LLM
# ============================================================

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0
)


# ============================================================
# SEARCH AGENT
# ============================================================

def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt=(
            "You are a professional web research agent. "
            "Use the web_search tool to find recent, reliable, "
            "and relevant information about the user's topic. "
            "Return useful findings and URLs that can be researched further."
        ),
        name="search_agent"
    )


# ============================================================
# READER AGENT
# ============================================================

def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt=(
            "You are a professional research reading agent. "
            "Given search results containing URLs, identify the "
            "most relevant URL and use the scrape_url tool to read "
            "the webpage. Extract important facts and information "
            "relevant to the research topic."
        ),
        name="reader_agent"
    )


# ============================================================
# WRITER CHAIN - LCEL
# ============================================================

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert research writer.

Write clear, structured, insightful, factual and professional
research reports.
"""
    ),
    (
        "human",
        """
Write a detailed research report on the topic below.

Topic:
{topic}

Research Gathered:
{research}

Structure the report as:

1. Introduction

2. Key Findings
   - Minimum 3 well-explained points

3. Conclusion

4. Sources
   - List all URLs found in the research

Be detailed, factual and professional.
"""
    )
])

writer_chain = writer_prompt | llm | StrOutputParser()


# ============================================================
# CRITIC CHAIN - LCEL
# ============================================================

critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are an expert research report critic.

Review the report for:

- factual clarity
- logical consistency
- completeness
- quality of explanation
- missing important information
- source usage

Give concise and actionable feedback.
"""
    ),
    (
        "human",
        """
Review the following research report:

{report}

Provide:

1. Overall assessment
2. Strengths
3. Problems or missing information
4. Specific improvements
"""
    )
])

critic_chain = critic_prompt | llm | StrOutputParser()