# filebundler/ui/tabs/global_settings_panel.py
import streamlit as st

from filebundler.ui.notification import show_temp_notification
from filebundler.managers.GlobalSettingsManager import GlobalSettingsManager


def render_global_settings(gsm: GlobalSettingsManager):
    """Render the global settings tab"""
    st.header("Global Settings")

    gsm.settings.max_files = st.number_input(
        "Default max files to display",
        min_value=10,
        value=gsm.settings.max_files,
    )

    st.subheader("Default Ignore Patterns")
    st.write("Default patterns for ignoring files in new projects (glob syntax)")

    with st.expander("Show/Hide Ignore Patterns", expanded=False):
        updated_patterns = st.text_area(
            "Edit default ignore patterns",
            "\n".join(gsm.settings.ignore_patterns),
        )

        if updated_patterns:
            gsm.settings.ignore_patterns = updated_patterns.split("\n")

    if st.button("Save Global Settings"):
        success = gsm.save_settings()
        if success:
            show_temp_notification("Global settings saved", type="success")
        else:
            show_temp_notification("Error saving global settings", type="error")
