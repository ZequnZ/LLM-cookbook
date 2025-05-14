# LLM Cookbook

A knowledge base for learning and experimenting with Large Language Models (LLMs).

## Structure

- `src/llm_cookbook/`: Main package code
  - `technologies/`: Technology-specific implementations
    - `openai_agents/`: OpenAI Agents SDK examples
    - `mcp/`: Model Control Protocol examples
  - `utils/`: Common utilities and helpers
- `notebooks/`: Jupyter notebooks for learning and experimentation


## Install Python decpendencies locally using `uv`

Here we use *uv* to have a smooth experience, it handles the Python environment and dependencies for us. It is a wrapper around *poetry* and *pyenv*.

### uv installation
Follow [this introduction](https://docs.astral.sh/uv/getting-started/installation) to install uv and you can also enable the tab completion for it for the terminal you use.

After that, move to the root directory of this repo and install a local Python environment:
```shell
uv sync
```

## License

MIT
