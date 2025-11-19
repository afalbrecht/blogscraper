#!/usr/bin/env python3
"""
Test Substack credentials from .env file.

This script verifies that your Substack session cookies are valid
by attempting to access Substack with authentication.
"""

import os
import sys
import requests
from dotenv import load_dotenv

def test_substack_credentials():
    """Test if Substack credentials are valid."""
    print("=" * 70)
    print("SUBSTACK CREDENTIALS TEST")
    print("=" * 70)
    print()
    
    # Load environment variables
    load_dotenv()
    
    # Get credentials
    substack_sid = os.getenv('SUBSTACK_SID')
    substack_lli = os.getenv('SUBSTACK_LLI')
    
    # Check if credentials exist
    if not substack_sid or not substack_lli:
        print("❌ ERROR: Credentials not found in .env file")
        print()
        print("Please ensure your .env file contains:")
        print("  SUBSTACK_SID=<your_session_id>")
        print("  SUBSTACK_LLI=<your_login_identifier>")
        print()
        print("Run 'python get_cookies.py' for instructions on how to get these values.")
        return False
    
    # Show credential info (partially masked for security)
    print("✓ Found credentials in .env file:")
    print(f"  SUBSTACK_SID: {substack_sid[:10]}...{substack_sid[-10:] if len(substack_sid) > 20 else ''}")
    print(f"  SUBSTACK_LLI: {substack_lli[:10]}...{substack_lli[-10:] if len(substack_lli) > 20 else ''}")
    print()
    
    # Test credentials by making a request to Substack
    print("Testing credentials with Substack...")
    
    try:
        # Create session with cookies
        session = requests.Session()
        session.cookies.set('substack.sid', substack_sid, domain='.substack.com')
        session.cookies.set('substack.lli', substack_lli, domain='.substack.com')
        
        # Try multiple test endpoints
        # First, try to get user info
        test_url = "https://substack.com/api/v1/reader/me"
        print(f"   Trying {test_url}...")
        response = session.get(test_url, timeout=10)
        
        if response.status_code == 200:
            # Try to parse response
            try:
                data = response.json()
                # If we got JSON data with user info, we're authenticated
                if data and ('email' in data or 'name' in data or 'id' in data):
                    print("✅ SUCCESS: Credentials are valid!")
                    print()
                    if 'email' in data:
                        print(f"   Authenticated as: {data.get('email', 'Unknown')}")
                    if 'name' in data:
                        print(f"   Name: {data.get('name', 'Unknown')}")
                    print()
                    print("You can now scrape paywalled Substack content!")
                    return True
            except Exception:
                pass
        
        # If first endpoint didn't work, try another approach
        # Try to access a known Substack's subscriber-only content
        print("   Trying alternative verification method...")
        
        # Test with a generic endpoint that should return different results for authenticated users
        test_url2 = "https://substack.com/api/v1/reader/subscriptions"
        response2 = session.get(test_url2, timeout=10)
        
        if response2.status_code == 200:
            try:
                data2 = response2.json()
                # If we get subscription data, we're likely authenticated
                if isinstance(data2, (list, dict)):
                    print("✅ SUCCESS: Credentials appear to be valid!")
                    print()
                    print("   Successfully retrieved subscription data from Substack.")
                    if isinstance(data2, list):
                        print(f"   Found {len(data2)} subscription(s).")
                    print()
                    print("You can now scrape paywalled Substack content!")
                    return True
            except Exception:
                pass

                
        elif response.status_code == 401 or response.status_code == 403:
            print("❌ FAILED: Credentials appear to be invalid or expired")
            print()
            print("Possible reasons:")
            print("  - Cookies have expired (Substack sessions expire after some time)")
            print("  - Cookies were copied incorrectly")
            print("  - You logged out from Substack in your browser")
            print()
            print("Solution:")
            print("  1. Log in to Substack in your browser")
            print("  2. Extract fresh cookies (run 'python get_cookies.py' for instructions)")
            print("  3. Update your .env file with the new values")
            return False
        else:
            print(f"⚠️  INCONCLUSIVE: API endpoints returned status code {response.status_code}")
            print()
            print("   The Substack API structure may have changed.")
            print("   Your credentials appear to be properly formatted:")
            print(f"     - SUBSTACK_SID is {len(substack_sid)} characters")
            print(f"     - SUBSTACK_LLI is {len(substack_lli)} characters")
            print()
            print("   RECOMMENDED: Test with actual blog scraping:")
            print("     python main.py --url https://example.substack.com --type substack")
            print()
            print("   If you can see full paywalled content in the PDF, your credentials work!")
            return None

            
    except requests.Timeout:
        print("⚠️  ERROR: Request timed out")
        print("   Check your internet connection and try again.")
        return None
    except requests.RequestException as e:
        print(f"⚠️  ERROR: Network error - {e}")
        print("   Check your internet connection and try again.")
        return None
    except Exception as e:
        print(f"⚠️  ERROR: Unexpected error - {e}")
        return None

if __name__ == "__main__":
    print()
    result = test_substack_credentials()
    print()
    print("=" * 70)
    
    if result is True:
        sys.exit(0)  # Success
    elif result is False:
        sys.exit(1)  # Definite failure
    else:
        sys.exit(2)  # Uncertain
