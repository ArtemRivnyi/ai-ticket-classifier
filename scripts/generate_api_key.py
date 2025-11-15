#!/usr/bin/env python3
"""
API Key Generator Script
Generates API keys for new clients
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth.api_keys import api_key_manager


def main():
    parser = argparse.ArgumentParser(
        description='Generate API keys for AI Ticket Classifier'
    )
    
    parser.add_argument(
        'client_name',
        help='Name of the client or organization'
    )
    
    parser.add_argument(
        '--tier',
        choices=['free', 'starter', 'professional', 'enterprise'],
        default='free',
        help='Subscription tier (default: free)'
    )
    
    parser.add_argument(
        '--email',
        help='Client email address'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all existing API keys'
    )
    
    args = parser.parse_args()
    
    # List keys if requested
    if args.list:
        print("\n" + "="*60)
        print("EXISTING API KEYS")
        print("="*60)
        
        keys = api_key_manager.list_keys(active_only=False)
        
        if not keys:
            print("No API keys found.")
        else:
            for key in keys:
                status = "✓ Active" if key['active'] else "✗ Inactive"
                print(f"\n{status} - {key['client_name']}")
                print(f"  Tier: {key['tier']}")
                print(f"  Created: {key['created_at']}")
                print(f"  Usage: {key['usage']['this_month']} requests this month")
                print(f"  Key Hash: {key['key_hash']}")
        
        print("\n" + "="*60)
        return
    
    # Generate new key
    print("\n" + "="*60)
    print("GENERATING NEW API KEY")
    print("="*60)
    print(f"Client Name: {args.client_name}")
    print(f"Tier: {args.tier}")
    if args.email:
        print(f"Email: {args.email}")
    print("="*60)
    
    try:
        # Generate the key
        api_key = api_key_manager.generate_key(
            client_name=args.client_name,
            tier=args.tier,
            email=args.email
        )
        
        # Get limits for this tier
        limits = api_key_manager.TIER_LIMITS[args.tier]
        
        print("\n✓ API Key Generated Successfully!")
        print("\n" + "="*60)
        print("API KEY (SAVE THIS SECURELY)")
        print("="*60)
        print(f"\n{api_key}\n")
        print("="*60)
        print("\nTHIS KEY WILL NOT BE SHOWN AGAIN!")
        print("Store it in a secure location.\n")
        print("="*60)
        print("RATE LIMITS")
        print("="*60)
        print(f"Requests per minute: {limits['requests_per_minute']}")
        print(f"Requests per hour: {limits['requests_per_hour']}")
        print(f"Requests per day: {limits['requests_per_day']}")
        print(f"Monthly quota: {limits['monthly_quota']}")
        print("="*60)
        print("\nUSAGE")
        print("="*60)
        print("Include this header in your API requests:")
        print(f"X-API-Key: {api_key}")
        print("\nExample curl command:")
        print(f"""
curl -X POST http://localhost:5000/api/v1/classify \\
  -H "X-API-Key: {api_key}" \\
  -H "Content-Type: application/json" \\
  -d '{{"ticket": "Cannot connect to VPN"}}'
        """)
        print("="*60 + "\n")
        
    except ValueError as e:
        print(f"\n✗ Error: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()