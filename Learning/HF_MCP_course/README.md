# Hugging Face MCP Course

link: https://huggingface.co/learn/mcp-course

Remember to put your HF TOKEN in `.env`.

### Tiny Agents from Hugging Face
I tried out [Tiny Agents](https://huggingface.co/blog/python-tiny-agents) and have the config in [my-agent](./my-agent/) folder

To run the agent:
```bash
uv run tiny-agents run agent.json
```

Example usage:
```
1. Using playwright, navigate to https://news.ycombinator.com.

2. Extract the titles and URLs of the top 4 posts on the homepage.

3. Create a file named hn.txt in the root directory of the project.

4. Save this list as plain text in the hn.txt file, with each line containing the title and URL separated by a hyphen.

Do not output code or instructions—just complete the task and confirm when it is done.
```

### Smolagent
Tried out [smolagent](https://github.com/huggingface/smolagents) to interact with inputs.

### HF Inference provider
https://huggingface.co/settings/inference-providers
