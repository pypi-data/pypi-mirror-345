import logging
import os

import streamlit as st

from common import GlobalState, CompletionsManager, ConfigManager


def main():
    logging.basicConfig(
        level=logging.DEBUG if int(os.environ.get("DEBUG", 0)) else logging.WARNING,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if "global_state" not in st.session_state:
        st.session_state.global_state = GlobalState(completions_manager=CompletionsManager())
        st.session_state.global_state.completions_manager.request(integration_ids=list(ConfigManager.get_config().integrations.keys()))

    st.set_page_config(page_title="StatQL", page_icon="📊", layout="wide")
    st.title("📊 StatQL")
    st.divider()

    pg = st.navigation([st.Page("query_console.py", title="📟 Query Console"), st.Page("integrations.py", title="🔌 Integrations")])
    pg.run()


if __name__ == "__main__":
    main()
