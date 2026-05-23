"""
End-to-end test: run the orchestrator with a math exclusion
to verify the full pipeline works with section exclusions.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from orchestrator import process_query


async def main():
    query = "Explain Newton's second law, do not give any math"
    print("=" * 60)
    print("  End-to-End Exclusion Test")
    print("=" * 60)
    print(f"\nQuery: {query}")
    print(f"Expected: math section should be EXCLUDED\n")
    print("-" * 60)

    result = await process_query(query, use_demo=False)

    synthesized = result.get("synthesized", "")
    print(synthesized[:3000].encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
    print("-" * 60)

    # Quick check
    has_math = "## " in synthesized and "Math" in synthesized
    if has_math:
        print("\n[WARNING] Math section may still be present in output!")
    else:
        print("\n[OK] Math section appears to be excluded as expected.")


if __name__ == "__main__":
    asyncio.run(main())
