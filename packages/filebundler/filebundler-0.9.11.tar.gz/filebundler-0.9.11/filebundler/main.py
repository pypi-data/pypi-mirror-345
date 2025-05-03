# filebundler/main.py
import logging
import os
import sys
import atexit
import argparse

from filebundler import app


def main():
    """Entry point function for the package."""

    # Register app.cleanup to be called on normal exit
    atexit.register(app.cleanup)

    parser = argparse.ArgumentParser(description="File Bundler App")
    subparsers = parser.add_subparsers(
        dest="command", help="Subcommands: web (default), cli"
    )

    # Web (default) subcommand
    parser_web = subparsers.add_parser(
        "web", help="Launch the FileBundler web app (default)"
    )
    parser_web.add_argument(
        "--headless", action="store_true", help="Run in headless mode"
    )
    parser_web.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Set the logging level (default: info)",
    )
    parser_web.add_argument(
        "--theme",
        default="dark",
        choices=["light", "dark"],
        help="Set the Streamlit theme (light or dark)",
    )

    # CLI subcommand
    parser_cli = subparsers.add_parser(
        "cli", help="Run CLI actions without starting the web server"
    )
    parser_cli.add_argument(
        "action", choices=["tree"], help="CLI action to perform (currently only 'tree')"
    )
    parser_cli.add_argument(
        "project_path",
        nargs="?",
        default=os.getcwd(),
        help="Path to the project root (default: current directory)",
    )
    parser_cli.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error", "critical"],
        help="Set the logging level (default: info)",
    )

    # If no subcommand is provided, default to 'web'
    if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] not in ["web", "cli"]):
        sys.argv.insert(1, "web")

    args = parser.parse_args()

    # Set log level
    if hasattr(args, "log_level") and args.log_level:
        os.environ["LOG_LEVEL"] = args.log_level

    if args.command == "cli":
        # CLI mode
        if args.action == "tree":
            from filebundler.services.project_structure import cli_entrypoint

            # Pass only the relevant arguments: script name and project_path
            cli_entrypoint([sys.argv[0], args.project_path])
            return
        else:
            import logging

            logger = logging.getLogger("filebundler.cli")
            logger.error(f"Unknown CLI action: {args.action}")
            print(f"Unknown CLI action: {args.action}")
            sys.exit(1)

    # Web mode (default)
    if "ANTHROPIC_API_KEY" not in os.environ:
        logging.warning(
            "\033[93mAnthropic API key not found in environment variables. "
            "Some features may not work as expected. "
            "(Color might not be supported in all terminals)\033[0m"
        )

    # When called as an installed package, we need to run Streamlit with this file
    import streamlit.web.cli as stcli

    # Get the absolute path to this file
    current_file = os.path.abspath(__file__)

    try:
        # Set up Streamlit arguments to run this file
        st_args = ["streamlit", "run", current_file, "--global.developmentMode=false"]
        if hasattr(args, "headless") and args.headless:
            st_args.append("--server.headless=true")
        if hasattr(args, "theme") and args.theme:
            st_args.append(f"--theme.base={args.theme}")

        sys.argv = st_args

        # Run Streamlit CLI with this file
        sys.exit(stcli.main())
    except KeyboardInterrupt:
        # Handle Ctrl+C at the top level
        logging.info("Keyboard interrupt received, exiting...")
        app.cleanup()
        sys.exit(0)


if __name__ == "__main__":
    atexit.register(app.cleanup)

    try:
        app.main()
    except KeyboardInterrupt:
        sys.exit(0)
