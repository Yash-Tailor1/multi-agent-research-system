import streamlit as st

from pipeline import (
    run_research_pipeline,
    PipelineStageError
)

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
# TITLE
# ============================================================

st.title("🔎 Multi-Agent Research System")

st.caption(
    "Tavily + BeautifulSoup + Groq Agents + LCEL"
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("📚 Research History")

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

        for search_id, topic_name, created_at in history:

            display_topic = topic_name

            if len(display_topic) > 35:
                display_topic = display_topic[:35] + "..."

            if st.button(
                f"🔎 {display_topic}",
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
# PREVIOUS SEARCH
# ============================================================

if st.session_state.selected_search_id:

    previous_search = get_search(
        st.session_state.selected_search_id
    )

    if previous_search:

        st.info(
            f"Viewing: **{previous_search['topic']}**"
        )

        st.subheader("📄 Research Report")

        st.markdown(
            previous_search["report"]
        )

        st.subheader("🧐 Critic Feedback")

        with st.expander(
            "View Critic Feedback"
        ):

            st.markdown(
                previous_search["feedback"]
            )

        with st.expander(
            "🔎 Tavily Search Results"
        ):

            st.write(
                previous_search["search_results"]
            )

        with st.expander(
            "🌐 Scraped Content"
        ):

            st.write(
                previous_search["scraped_content"]
            )

    st.stop()


# ============================================================
# NEW RESEARCH
# ============================================================

st.subheader("Research Topic")

topic = st.text_area(
    "What would you like me to research?",
    placeholder=(
        "Example: Impact of war on the stock market"
    ),
    height=100
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


    # ========================================================
    # LIVE STATUS
    # ========================================================

    st.subheader("⚡ Live Agent Status")

    search_status = st.empty()
    reader_status = st.empty()
    writer_status = st.empty()
    critic_status = st.empty()


    status_boxes = {
        "search": search_status,
        "reader": reader_status,
        "writer": writer_status,
        "critic": critic_status
    }


    def progress_callback(
        stage,
        status,
        message
    ):

        box = status_boxes[stage]

        if status == "running":

            box.info(
                f"🔄 **{stage.title()}** — {message}"
            )

        elif status == "complete":

            box.success(
                f"✅ **{stage.title()}** — {message}"
            )

        elif status == "error":

            box.error(
                f"❌ **{stage.title()}** — {message}"
            )


    try:

        with st.spinner(
            "Running multi-agent research..."
        ):

            result = run_research_pipeline(
                topic,
                progress_callback=progress_callback
            )


        st.success(
            "🎉 All agents completed successfully!"
        )


        # ====================================================
        # SAVE HISTORY
        # ====================================================

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

        st.session_state.selected_search_id = search_id


        # ====================================================
        # REPORT
        # ====================================================

        st.divider()

        st.subheader("📄 Final Research Report")

        st.markdown(
            result["report"]
        )


        # ====================================================
        # CRITIC
        # ====================================================

        st.subheader("🧐 Critic Feedback")

        with st.expander(
            "View Critic Feedback",
            expanded=True
        ):

            st.markdown(
                result["feedback"]
            )


        # ====================================================
        # RAW DATA
        # ====================================================

        with st.expander(
            "🔎 Tavily Search Results"
        ):

            st.write(
                result["search_results"]
            )


        with st.expander(
            "🌐 BeautifulSoup Content"
        ):

            st.write(
                result["scraped_content"]
            )


    except PipelineStageError as e:

        st.error(
            f"❌ Pipeline stopped at: **{e.stage}**"
        )

        st.code(
            f"{type(e.original_error).__name__}: "
            f"{e.original_error}",
            language="text"
        )

        st.warning(
            "The remaining stages were not executed."
        )


    except Exception as e:

        st.error(
            "❌ Unexpected pipeline error"
        )

        st.exception(e)