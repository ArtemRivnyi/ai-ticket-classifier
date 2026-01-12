#!/usr/bin/env python3
"""
Script to generate API keys for the AI Ticket Classifier.
Usage: python scripts/generate_api_key.py --user_id <user_id> --name <key_name> [--tier <tier>]
"""

import argparse
import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from middleware.auth import APIKeyManager
from dotenv import load_dotenv


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Generate API Key")
    parser.add_argument(
        "--user_id", required=True, help="User ID (e.g., email or uuid)"
    )
    parser.add_argument(
        "--name", required=True, help='Key name (e.g., "Development Key")'
    )
    parser.add_argument(
        "--tier",
        default="free",
        choices=["free", "starter", "professional", "enterprise"],
        help="Subscription tier",
    )

    args = parser.parse_args()

    try:
        print(f"Generating API key for user: {args.user_id} ({args.tier})...")
        result = APIKeyManager.create_key(args.user_id, args.name, args.tier)

        print("\n✅ API Key Generated Successfully!")
        print("-" * 50)
        print(f"Key:       {result['key']}")
        print(f"Key ID:    {result['key_id']}")
        print(f"Tier:      {result['tier']}")
        print(f"Created:   {result['created_at']}")
        print("-" * 50)
        print("⚠️  SAVE THIS KEY NOW! It cannot be retrieved later.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
