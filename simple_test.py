#!/usr/bin/env python3

import instaloader
import os
import sys

def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "mayankupadhyay3335"
    print(f"Attempting to get data for Instagram user: {username}")
    
    # Create an instance of Instaloader
    loader = instaloader.Instaloader()
    
    try:
        # Simple interactive login
        print("Please login in the browser window that opens...")
        loader.interactive_login(None)  # Will open browser
        print("Login successful!")
        
        # Get profile data
        profile = instaloader.Profile.from_username(loader.context, username)
        
        # Print basic profile info
        print("\n--- Profile Information ---")
        print(f"Username: {profile.username}")
        print(f"Full name: {profile.full_name}")
        print(f"Bio: {profile.biography}")
        print(f"Followers: {profile.followers}")
        print(f"Following: {profile.followees}")
        print(f"Posts: {profile.mediacount}")
        
        # Save followers to a file
        print("\nSaving followers list...")
        followers = []
        for follower in profile.get_followers():
            followers.append({
                "username": follower.username,
                "full_name": follower.full_name
            })
            print(f"Found follower: {follower.username}")
            if len(followers) >= 10:
                print("(Stopping at 10 followers for this test)")
                break
                
        print(f"\nTotal followers retrieved: {len(followers)}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
