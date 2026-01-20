#!/usr/bin/env python
"""
Quick reseed script for CARP database via API.

Usage:
    python reseed.py https://carp-hack4good.vercel.app YOUR_SEED_SECRET
    
Or for local development:
    python reseed.py http://localhost:5000 YOUR_SEED_SECRET
"""

import sys
import urllib.request
import urllib.error
import json

def reseed(base_url: str, seed_secret: str) -> None:
    """Call the seed API endpoint to reseed the database."""
    url = f"{base_url.rstrip('/')}/api/seed"
    
    print(f"🌱 Reseeding database at: {url}")
    
    data = json.dumps({"secret": seed_secret}).encode('utf-8')
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            print("\n✅ Database reseeded successfully!")
            print(f"\n📊 Summary:")
            if 'summary' in result:
                summary = result['summary']
                print(f"   • Users: {summary.get('users', 'N/A')}")
                print(f"   • Participants: {summary.get('participants', 'N/A')}")
                print(f"   • Events: {summary.get('events', 'N/A')}")
                print(f"   • Registrations: {summary.get('registrations', 'N/A')}")
            
            print("\n🔐 Demo Credentials:")
            print("   Admin: admin@carp.sg / admin123")
            print("   Caregiver: alice.tan@gmail.com / demo123")
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        print(f"\n❌ Error {e.code}: {error_body}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"\n❌ Connection error: {e.reason}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reseed.py <BASE_URL> <SEED_SECRET>")
        print("\nExample:")
        print("  python reseed.py https://carp-hack4good.vercel.app mysecret123")
        sys.exit(1)
    
    reseed(sys.argv[1], sys.argv[2])
