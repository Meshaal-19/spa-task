from dotenv import load_dotenv
from agent import run_agent
from memory import Memory

load_dotenv()


def main():
    memory = Memory()

    print("\n" + "=" * 60)
    print("DEMO 1: Web search + memory")
    print("=" * 60)
    run_agent(
        "Search for the latest news about Claude AI and remember the main topic you found",
        memory,
    )

    print("\n" + "=" * 60)
    print("DEMO 2: File reading")
    print("=" * 60)
    run_agent(
        "Read the file notes.txt and give me a summary of what it contains",
        memory,
    )

    print("\n" + "=" * 60)
    print("DEMO 3: Memory recall")
    print("=" * 60)
    run_agent("What did I ask you to remember earlier?", memory)


if __name__ == "__main__":
    main()
