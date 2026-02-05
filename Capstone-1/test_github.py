#!/usr/bin/env python3
"""
Test GitHub token validity
"""
import os
from dotenv import load_dotenv
from github import Github, Auth

load_dotenv()

token = os.getenv('GITHUB_TOKEN')
repo_name = os.getenv('GITHUB_REPO')

print("=" * 60)
print("GitHub Token Verification")
print("=" * 60)

if not token:
    print("❌ GITHUB_TOKEN not found in .env file")
    exit(1)

if not repo_name:
    print("❌ GITHUB_REPO not found in .env file")
    exit(1)

print(f"✓ Token found: {token[:10]}...{token[-4:]}")
print(f"✓ Token length: {len(token)} characters")
print(f"✓ Repository: {repo_name}")
print()

try:
    print("Testing GitHub connection...")
    auth = Auth.Token(token)
    g = Github(auth=auth)
    
    # Test authentication
    user = g.get_user()
    print(f"✅ Authenticated as: {user.login}")
    
    # Test repository access
    repo = g.get_repo(repo_name)
    print(f"✅ Repository access: {repo.full_name}")
    print(f"   Description: {repo.description or 'No description'}")
    print(f"   Private: {repo.private}")
    
    # Test permissions
    permissions = repo.permissions
    print(f"✅ Permissions:")
    print(f"   - Admin: {permissions.admin}")
    print(f"   - Push: {permissions.push}")
    print(f"   - Pull: {permissions.pull}")
    
    print()
    print("=" * 60)
    print("✅ GitHub integration is working correctly!")
    print("=" * 60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("=" * 60)
    print("TROUBLESHOOTING:")
    print("=" * 60)
    print("1. Your GitHub token may be expired or revoked")
    print("2. Generate a new token at: https://github.com/settings/tokens")
    print("3. Required scopes: 'repo' (full control of private repositories)")
    print("4. Update GITHUB_TOKEN in your .env file")
    print("5. Restart the application")
    print("=" * 60)
    exit(1)
