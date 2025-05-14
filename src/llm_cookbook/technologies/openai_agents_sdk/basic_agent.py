"""
Basic OpenAI Agent implementation
"""


class BasicAgent:
    """
    A basic implementation of an OpenAI Agent
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialize the agent

        Args:
            api_key: OpenAI API key. If None, will look for OPENAI_API_KEY in environment
        """
        from openai import OpenAI

        from llm_cookbook.utils.common_functions import load_environment_variables

        env_vars = load_environment_variables()
        self.api_key = api_key or env_vars.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found")

        self.client = OpenAI(api_key=self.api_key)

    def run(self, prompt: str) -> str:
        """
        Run the agent with a given prompt

        Args:
            prompt: The prompt to send to the agent

        Returns:
            The agent's response
        """
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
