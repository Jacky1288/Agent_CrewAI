#!/usr/bin/env python
import sys
import os
import warnings
from dotenv import load_dotenv, find_dotenv

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# Load .env before importing crew so MODEL and API keys are set
load_dotenv(find_dotenv())

from deep_research_crew.crew import ParallelDeepResearchCrew

# This main file is intended to be a way for your to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information


def run():
    """
    Run the crew.
    """
    ### START CODE HERE ###
    inputs = { 
        "user_query": "Evaluate the top one emerging AI tool for automating competitive market analysis, including its features, limitations, costs, and ideal use cases for a mid-sized marketing firm."
    }
    ### END CODE HERE ###
    ParallelDeepResearchCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'user_query': 'sample_value'
    }
    try:
        ParallelDeepResearchCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        ParallelDeepResearchCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'user_query': 'sample_value'
    }
    try:
        ParallelDeepResearchCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)