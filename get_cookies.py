#!/usr/bin/env python3
"""
Helper script to extract Substack session cookies from your browser.

This script provides instructions to manually extract the cookies needed
for Substack authentication.
"""

import sys

def print_instructions():
    print("=" * 70)
    print("SUBSTACK COOKIE EXTRACTION INSTRUCTIONS")
    print("=" * 70)
    print()
    print("To access paywalled Substack content, you need to extract session")
    print("cookies from your logged-in browser session.")
    print()
    print("STEP-BY-STEP GUIDE:")
    print()
    print("1. Open your web browser (Chrome, Firefox, etc.)")
    print()
    print("2. Navigate to: https://substack.com")
    print()
    print("3. Log in with your Substack account credentials")
    print()
    print("4. Once logged in, open Developer Tools:")
    print("   - Chrome/Edge: Press F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)")
    print("   - Firefox: Press F12 or Ctrl+Shift+I (Cmd+Option+I on Mac)")
    print()
    print("5. Navigate to the 'Application' tab (Chrome) or 'Storage' tab (Firefox)")
    print()
    print("6. In the left sidebar, expand 'Cookies' and click on 'https://substack.com'")
    print()
    print("7. Find these two cookies and copy their values:")
    print("   - substack.sid")
    print("   - substack.lli")
    print()
    print("8. Create a .env file in the blogscraper directory:")
    print()
    print("   Create a file named '.env' with this content:")
    print()
    print("   SUBSTACK_SID=<paste_the_value_of_substack.sid_here>")
    print("   SUBSTACK_LLI=<paste_the_value_of_substack.lli_here>")
    print()
    print("9. Save the .env file")
    print()
    print("10. Run your scraper as normal - it will now use authentication!")
    print()
    print("=" * 70)
    print()
    print("SECURITY NOTE:")
    print("The .env file is automatically excluded from git by .gitignore,")
    print("but be careful not to share it publicly as it contains your")
    print("login session credentials.")
    print()
    print("=" * 70)

if __name__ == "__main__":
    print_instructions()
