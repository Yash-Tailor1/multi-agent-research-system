from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain
)


class PipelineStageError(Exception):

    def __init__(self, stage, original_error):

        self.stage = stage
        self.original_error = original_error

        super().__init__(
            f"{stage} failed: "
            f"{type(original_error).__name__}: "
            f"{original_error}"
        )


def run_research_pipeline(
    topic: str,
    progress_callback=None
) -> dict:

    state = {}

    def update(stage, status, message):

        if progress_callback:
            progress_callback(
                stage,
                status,
                message
            )


    # ============================================================
    # STEP 1 - SEARCH AGENT
    # ============================================================

    update(
        "search",
        "running",
        "Search Agent is starting..."
    )

    try:

        search_agent = build_search_agent()

        update(
            "search",
            "running",
            "Groq is reasoning and calling Tavily..."
        )

        search_result = search_agent.invoke({
            "messages": [
                (
                    "user",
                    f"""
Find recent, reliable and relevant information
about the following topic:

{topic}

Use the web_search tool.
Return concise findings and useful URLs.
"""
                )
            ]
        })

        state["search_results"] = (
            search_result["messages"][-1].content
        )

        update(
            "search",
            "complete",
            "Search Agent completed successfully."
        )

    except Exception as e:

        update(
            "search",
            "error",
            f"{type(e).__name__}: {e}"
        )

        raise PipelineStageError(
            "Search Agent",
            e
        ) from e


    # ============================================================
    # STEP 2 - READER AGENT
    # ============================================================

    update(
        "reader",
        "running",
        "Reader Agent is starting..."
    )

    try:

        reader_agent = build_reader_agent()

        # Keep search context small
        compact_search = state["search_results"][:1800]

        update(
            "reader",
            "running",
            "Reader Agent is selecting and scraping a source..."
        )

        reader_result = reader_agent.invoke({
            "messages": [
                (
                    "user",
                    f"""
Topic:
{topic}

Search Results:
{compact_search}

Choose the most relevant URL and use the scrape_url
tool to extract deeper information.

Keep the final response concise.
"""
                )
            ]
        })

        state["scraped_content"] = (
            reader_result["messages"][-1].content
        )

        update(
            "reader",
            "complete",
            "Reader Agent completed successfully."
        )

    except Exception as e:

        update(
            "reader",
            "error",
            f"{type(e).__name__}: {e}"
        )

        raise PipelineStageError(
            "Reader Agent",
            e
        ) from e


    # ============================================================
    # STEP 3 - WRITER
    # ============================================================

    update(
        "writer",
        "running",
        "Writer Chain is generating the report..."
    )

    try:

        # IMPORTANT:
        # Limit the amount of context sent to Groq.

        search_for_writer = state["search_results"][:1500]

        scraped_for_writer = state["scraped_content"][:2000]

        research_combined = (
            f"SEARCH RESULTS:\n"
            f"{search_for_writer}\n\n"
            f"SCRAPED CONTENT:\n"
            f"{scraped_for_writer}"
        )

        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined
        })

        update(
            "writer",
            "complete",
            "Writer Chain completed successfully."
        )

    except Exception as e:

        update(
            "writer",
            "error",
            f"{type(e).__name__}: {e}"
        )

        raise PipelineStageError(
            "Writer Chain",
            e
        ) from e


    # ============================================================
    # STEP 4 - CRITIC
    # ============================================================

    update(
        "critic",
        "running",
        "Critic Chain is reviewing the report..."
    )

    try:

        state["feedback"] = critic_chain.invoke({
            "report": state["report"][:4000]
        })

        update(
            "critic",
            "complete",
            "Critic Chain completed successfully."
        )

    except Exception as e:

        update(
            "critic",
            "error",
            f"{type(e).__name__}: {e}"
        )

        raise PipelineStageError(
            "Critic Chain",
            e
        ) from e


    return state