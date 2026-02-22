import streamlit as st


def run() -> None:
    st.set_page_config(
        page_title="Dishing Out Data",
        page_icon="D",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("Dishing Out Data")
    st.caption("Choose a dashboard. Each city page is filtered by state only.")

    apps = {
        "City Dashboards": [
            st.Page("apps/austin/austin.py", title="Austin"),
            st.Page("apps/chicago/chicago.py", title="Chicago"),
            st.Page("apps/new_york/new_york.py", title="New York"),
            st.Page("apps/los_angeles/los_angeles.py", title="Los Angeles"),
        ]
    }

    pg = st.navigation(apps)
    pg.run()


if __name__ == "__main__":
    run()
