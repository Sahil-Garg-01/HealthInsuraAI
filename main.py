"""
Health Insurance Claim Processing System.

Entry point for running the claim processing agent.
"""

import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Run the claim processing system."""
    from src.agent.react_agent import run_agent
    
    logger.info("Health Insurance Claim System Starting...")
    
    # Example: Process sample claim files
    sample_files = ["sample_claim.pdf", "sample_bill.pdf"]
    
    result = run_agent(sample_files)
    
    logger.info("Processing complete")
    print(f"\nDecision: {result['decision']}")
    print(f"Iterations: {result['iterations']}")
    print(f"\nFinal Response:\n{result['final_response']}")


if __name__ == "__main__":
    main()