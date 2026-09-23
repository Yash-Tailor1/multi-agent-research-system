
import streamlit as st

from pipeline import run_research_pipeline
from history import (
    get_search_history,
    get_search,
    save_search,
    clear_history
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "selected_search_id" not in st.session_state:
    st.session_state.selected_search_id = None


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        color: #6b7280;
        margin-bottom: 25px;
    }

    .history-item {
        padding: 8px 0;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🔎 Research History")

    st.caption("Previous research searches")

    # New research button
    if st.button(
        "➕ New Research",
        use_container_width=True
    ):

        st.session_state.selected_search_id = None
        st.rerun()

    st.divider()

    history = get_search_history()

    if not history:

        st.info("No previous searches yet.")

    else:

        for search_id, topic, created_at in history:

            # Shorten long topics for sidebar
            display_topic = topic

            if len(display_topic) > 38:
                display_topic = display_topic[:38] + "..."

            label = f"🔎 {display_topic}"

            if st.button(
                label,
                key=f"history_{search_id}",
                use_container_width=True
            ):

                st.session_state.selected_search_id = search_id
                st.rerun()

            st.caption(created_at)

    st.divider()

    if history:

        if st.button(
            "🗑️ Clear History",
            use_container_width=True
        ):

            clear_history()

            st.session_state.selected_search_id = None

            st.rerun()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🔎 Multi-Agent Research System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Tavily + BeautifulSoup + Groq Agents + LCEL'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SHOW PREVIOUS SEARCH
# ============================================================

if st.session_state.selected_search_id:

    previous_search = get_search(
        st.session_state.selected_search_id
    )

    if previous_search:

        st.info(
            f"📚 Viewing previous research: "
            f"**{previous_search['topic']}**"
        )

        st.caption(
            f"Created: {previous_search['created_at']}"
        )

        st.divider()

        # Report
        st.subheader("📄 Research Report")

        st.markdown(
            previous_search["report"] or
            "No report available."
        )

        # Critic
        st.subheader("🧐 Critic Feedback")

        with st.expander(
            "View Critic Feedback",
            expanded=False
        ):

            st.markdown(
                previous_search["feedback"] or
                "No feedback available."
            )

        # Search results
        with st.expander(
            "🔎 View Tavily Search Results"
        ):

            st.write(
                previous_search["search_results"] or
                "No search results available."
            )

        # Scraped content
        with st.expander(
            "🌐 View Scraped Content"
        ):

            st.write(
                previous_search["scraped_content"] or
                "No scraped content available."
            )

        st.divider()

        st.download_button(
            "⬇️ Download Report",
            data=previous_search["report"],
            file_name="research_report.txt",
            mime="text/plain",
            use_container_width=True
        )


# ============================================================
# NEW RESEARCH
# ============================================================

else:

    st.subheader("Research Topic")

    topic = st.text_area(
        "What would you like me to research?",
        height=100,
        placeholder=(
            "Example: What is the impact of war "
            "on the stock market?"
        )
    )

    research_button = st.button(
        "🔍 Start Research",
        type="primary",
        use_container_width=True
    )

    if research_button:

        if not topic.strip():

            st.warning(
                "Please enter a research topic."
            )

            st.stop()

        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        st.subheader("Research Progress")

        progress = st.progress(0)

        status = st.empty()

        try:

            status.info(
                "🔎 Search Agent is researching..."
            )

            progress.progress(20)

            with st.spinner(
                "Running multi-agent research pipeline..."
            ):

                result = run_research_pipeline(topic)

            progress.progress(100)

            status.success(
                "✅ Research completed successfully."
            )

            # ------------------------------------------------
            # SAVE TO DATABASE
            # ------------------------------------------------

            search_id = save_search(
                topic=topic,
                search_results=result.get(
                    "search_results",
                    ""
                ),
                scraped_content=result.get(
                    "scraped_content",
                    ""
                ),
                report=result.get(
                    "report",
                    ""
                ),
                feedback=result.get(
                    "feedback",
                    ""
                )
            )

            # Automatically select the new search
            st.session_state.selected_search_id = search_id

            st.success(
                "✅ Research saved to history."
            )

            st.rerun()

        except Exception as e:

            progress.empty()

            status.error(
                "❌ Research pipeline failed."
            )

            st.exception(e)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Powered by LangChain • LangGraph • Groq • Tavily • BeautifulSoup"
)

