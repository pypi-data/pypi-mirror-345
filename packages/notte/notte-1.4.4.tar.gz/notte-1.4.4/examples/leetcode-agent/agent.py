from dotenv import load_dotenv
from notte_agent import Agent
from notte_sdk import NotteClient

_ = load_dotenv()


def main():
    # Load environment variables and create vault
    # Required environment variable:
    # - NOTTE_API_KEY: your api key for the sdk
    # - LEETCODE_COM_USERNAME: your leetcode username
    # - LEETCODE_COM_PASSWORD: your leetcode password
    # - NOTTE_API_KEY: your api key for the sdk
    client = NotteClient()
    with client.vaults.create() as vault:
        vault.add_credentials_from_env("leetcode.com")
        agent: Agent = Agent(vault=vault)
        response = agent.run(
            task=(
                "Go to leetcode.com and solve the problem of the day. when you arrive on the page change the programming language to python."
                "First login to leetcode and then resolve the problem of the day"
                "When there is a cloudflare challenge, click on the box to verify that you are human"
            )
        )
        print(response)


if __name__ == "__main__":
    main()
