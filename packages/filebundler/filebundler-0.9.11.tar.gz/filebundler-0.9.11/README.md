# FileBundler

```bash
uvx filebundler #  -> will automatically open a browser window!
uvx filebundler web --headless #  -> no auto open
uvx filebundler web --theme #  -> light|dark
uvx filebundler web --log-level debug #  or one of [debug|info|warning|error|critical]

# CLI usage (new!)
uvx filebundler cli tree [project_path] #  -> generates .filebundler/project-structure.md for the given project (default: current directory)
uvx filebundler web [options]           #  -> launches the web app (default if no subcommand)
```

## What is it?
File Bundler is a web app and CLI utility to bundle project files together and use them for LLM prompting. It helps estimate and optimize token and context usage.

# Who is FileBundler for?
If you're used to copying your files into your "chat of choice" and find the output is often better than the edits your AI powered IDE proposes then FileBundler is for you.

**Here are some reasons why:**
1. Segment your projects into topics (manually or with AI)
2. Optimize your LLM context usage
3. Copy fresh context in one click, no uploading files, no "Select a file..." dialog
4. It encourages you to use best practices, like [anthropic's use of xml tags](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/use-xml-tags)

# How do I use it?
- install and run FileBundler per the command at the start of this README
- visit the URL shown on your terminal
- you'll be prompted to enter the path of your project (this is your local filesystem path)
  - you can copy the path to your folder and paste it there
  - <details><summary>why no file selection window</summary>we currently don't support a "Select file" dialog but we're open to it if this is a major pain point</details>
- This will load the <span style="color:green">file tree 🌳</span> on the sidebar and the tabs on the right
- The tabs will display your currently selected files, allow you to save them in a bundle and export their contents to be pasted on your chat of preference
- To save a bundle you need to enter a name. The name must be lowercase and include only hyphens ("-") letters and numbers

# Features
Besides creating bundles FileBundler has additional features

## Project Structure
The app automatically exports your project structure to a file called `project-structure.md` in the `.filebundler` folder. In the `Project Settings` tab on the sidebar you can add or remove glob patterns to ignore certain files or folders from the project structure. These patterns are taken into account for the whole app (i.e. the file tree, the auto-bundler and the project structure export).

## Estimate token usage
We currently use tiktoken with the [o200k_base](https://github.com/openai/tiktoken) model to estimate token count, but you can may a utility like [tokencounter.org](https://tokencounter.org/) to estimate token usage for other models or [openai's tokenizer](https://platform.openai.com/tokenizer) to compare estimates.

## Auto-Bundle
The auto-bundler is a feature that uses an LLM to suggest you bundles relevant to your query. The auto-bundler automatically selects your exported project structure (which you can unselect if you want to).

The auto-bundler will use your prompt and current selections to suggest bundles. The LLM will return a list of likely and probable files that are relevant to your query, and a message and/or code if you asked for it.

A workflow example would be for you to provide the LLM with your TODO list (TODO.md) and ask it to provide you with the files that are related to the first n tasks. You could also ask it to sort your tasks into different categories and then re-prompt it to provide bundles for each category.

Right now the auto-bundler uses Anthropic as a provider. If the app doesn't find an `ANTHROPIC_API_KEY` in your environment variables it will display an input field to enter it manually. All latest models from Anthropic are supported. (as of today 21 Mar 2025). As this is an open source project, more providers and models will be added if there's a need for them.

# Roadmap
[TODO.md](https://raw.githubusercontent.com/dsfaccini/filebundler/refs/heads/master/TODO.md)
We plan on adding other features, like codebase indexing

# Performance and debugging
If your application **doesn't start or freezes** you can check the logs in your terminal.

If your application **hangs** on certain actions, you can debug using logfire. For this you'll need to stop FileBundler, set your logfire token and re-run the app.

You can set your logfire token like this
<details>
<summary>Unix/macOS</summary>

```bash
export LOGFIRE_TOKEN=your_token_here
```
</details>

<details>
<summary>Windows</summary>

```powershell
# using cmd
set LOGFIRE_TOKEN=your_token_here

# or in PowerShell
$env:LOGFIRE_TOKEN = "your_token_here"
```
</details>

For any other issues you may open an issue in the [filebundler repo](https://github.com/dsfaccini/filebundler).

# Similar tools

## [Cursor](https://www.cursor.com/)
Currently, you can add project rules to your project and include globs for files related to those rules. This is kind of a reverse file bundler, since cursor uses the files in the glob to determine what rules you send to the LLM.
You can as well make a selection of files to be included in a chat, but you don't have an overview of how much context has been used. To clear the context you can start a new chat, but the selection you made for the previous chat won't be persisted (as of today), so you need to reselect your files.

## RepoPrompt
Before I started this tool I researched if there was already an existing tool and stumbled upon [Repo Prompt](https://x.com/RepoPrompt), which I believe is built by @pvncher. Some reasons I decided against using it were:
1. currently waitlisted
2. currently not available for Windows
3. closed source
4. pricing

For the record it seems like a great tool and I invite you to check it out. It offers lots of other functionality, like diffs and code trees.

## [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview)
Like cursor but on the CLI. With the introduction of [commands](https://x.com/_catwu/status/1900593730538864643) you can save markdown files with your prompts and issue them as commands to claude code. This is a bit different than bundling project files into topics, but shares the concept of persisting workflows that you repeat as settings.

## aider
TODO

# Useful references
- [anthropic's prompt library](https://docs.anthropic.com/en/prompt-library)
- [anthropic's long context tips](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips#example-multi-document-structure)

# LICENSE
We use GPLv3. Read it [here](https://raw.githubusercontent.com/dsfaccini/filebundler/refs/heads/master/LICENSE)

## CLI Usage

FileBundler now supports a CLI mode for project actions without starting the web server.

- To generate the project structure markdown file for your project, run:

```bash
uvx filebundler cli tree [project_path]
```
- `project_path` is optional; if omitted, the current directory is used.
- The output will be saved to `.filebundler/project-structure.md` in your project.

- To launch the web app (default):

```bash
uvx filebundler web [options]
```

- If you run `uvx filebundler` with no subcommand, it defaults to `web` mode.