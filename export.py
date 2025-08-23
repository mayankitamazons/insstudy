#!/usr/bin/env python3
"""
Instagram Data Exporter - A simplified version of InstaTracker
Created by: https://github.com/ibnaleem
Modified for JSON data export only
"""

import instaloader
import os
import json
import sys
import datetime
import time
import requests
import argparse
from rich.console import Console

def fetch_graphql_data(query_hash, variables, output_file=None, console=None):
    """
    Fetch data directly from Instagram GraphQL API endpoint
    
    Args:
        query_hash: The GraphQL query hash
        variables: Dict or JSON string of variables to send
        output_file: Where to save the output (defaults to query_hash.json)
        console: Rich console instance for output
    """
    if console is None:
        console = Console()
        
    # Convert variables to string if they're a dict
    if isinstance(variables, dict):
        variables = json.dumps(variables)
        
    if output_file is None:
        output_file = f"{query_hash}_data.json"
    
    # Set up headers to look like a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.instagram.com/',
        'X-IG-App-ID': '936619743392459',  # Common Instagram App ID
        'X-Requested-With': 'XMLHttpRequest',
    }
    
    # Try to get cookies from browser for authentication
    try:
        import browser_cookie3
        cookies = browser_cookie3.chrome(domain_name='.instagram.com')
        console.print("[green]Successfully retrieved cookies from Chrome browser[/green]")
    except Exception as e:
        console.print(f"[yellow]Could not get browser cookies: {e}[/yellow]")
        console.print("[yellow]Proceeding without authentication, which may limit access[/yellow]")
        cookies = None
    
    url = f"https://www.instagram.com/graphql/query?query_hash={query_hash}&variables={variables}"
    
    console.print(f"[bold blue]Fetching data from Instagram GraphQL API...[/bold blue]")
    console.print(f"[yellow]URL: {url}[/yellow]")
    
    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Save the data to a file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                
            console.print(f"[bold green]✅ Data successfully saved to {output_file}[/bold green]")
            
            # Try to print some summary info about the data
            if 'data' in data:
                if 'user' in data['data']:
                    user = data['data']['user']
                    if user:
                        console.print("[green]User data retrieved successfully[/green]")
            
            return data
        else:
            console.print(f"[bold red]Error: HTTP {response.status_code}[/bold red]")
            console.print(f"[yellow]Response: {response.text[:200]}...[/yellow]")
            
            if response.status_code == 401:
                console.print("[bold red]Authentication error. Make sure you are logged into Instagram in Chrome[/bold red]")
            elif response.status_code == 429:
                console.print("[bold red]Rate limited by Instagram. Try again later.[/bold red]")
                
            return None
            
    except Exception as e:
        console.print(f"[bold red]Error fetching data: {e}[/bold red]")
        return None

def main():
    console = Console()
    
    # Use argparse for better command-line argument handling
    parser = argparse.ArgumentParser(description="Instagram Data Exporter")
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Subparser for the original user data export
    user_parser = subparsers.add_parser('user', help='Export user data using instaloader')
    user_parser.add_argument('username', help='Instagram username to export data for')
    
    # Subparser for the new GraphQL data fetching
    graphql_parser = subparsers.add_parser('graphql', help='Fetch data directly from Instagram GraphQL API')
    graphql_parser.add_argument('--query-hash', default='37479f2b8209594dde7facb0d904896a', 
                              help='GraphQL query hash (default: 37479f2b8209594dde7facb0d904896a)')
    graphql_parser.add_argument('--variables', default='{"id":"7093386149","first":12}',
                              help='GraphQL variables as JSON string')
    graphql_parser.add_argument('--output', help='Output JSON filename')
    
    args = parser.parse_args()
    
    # If no arguments were provided, show help
    if not args.command:
        parser.print_help()
        return
    
    # Handle GraphQL command
    if args.command == 'graphql':
        fetch_graphql_data(args.query_hash, args.variables, args.output, console)
        return
    
    # Original functionality for user data export
    username = args.username
    console.print(f"[bold blue]Instagram Data Exporter for user: {username}[/bold blue]")
    
    # Create Instaloader instance
    loader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )
    
    # Attempt login
    try:
        session_file = f"{os.path.expanduser('~')}/.instaloader_session"
        
        # Try to load existing session
        if os.path.exists(session_file):
            console.print("[yellow]Loading existing session...[/yellow]")
            try:
                loader.load_session_from_file(None, session_file)
                console.print("[green]Session loaded successfully![/green]")
            except Exception:
                console.print("[yellow]Existing session invalid, will try interactive login...[/yellow]")
                loader.interactive_login(None)  # Will open browser
        else:
            console.print("[yellow]No session found, starting interactive login...[/yellow]")
            loader.interactive_login(None)  # Will open browser
            
        # Try to save the session
        try:
            loader.save_session_to_file(session_file)
        except Exception:
            console.print("[yellow]Note: Could not save session file[/yellow]")
    
    except Exception as e:
        console.print(f"[bold red]Login failed: {e}[/bold red]")
        return
        
    # Get profile
    try:
        console.print("[yellow]Loading profile data...[/yellow]")
        profile = instaloader.Profile.from_username(loader.context, username)
        
        # Create output directory if it doesn't exist
        output_dir = f"{username}_data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Get timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save account info
        account_info = {
            "timestamp": timestamp,
            "username": username,
            "full_name": profile.full_name,
            "biography": profile.biography,
            "followers_count": profile.followers,
            "following_count": profile.followees,
            "posts_count": profile.mediacount,
            "is_private": profile.is_private,
            "is_verified": profile.is_verified,
            "profile_pic_url": profile.profile_pic_url
        }
        
        with open(f"{output_dir}/account_info.json", "w") as f:
            json.dump(account_info, f, indent=4)
        console.print(f"[green]Account info saved to {output_dir}/account_info.json[/green]")
        
        # Get followers
        if not profile.is_private:
            console.print("[yellow]Downloading followers list (this may take time)...[/yellow]")
            followers = []
            count = 0
            
            for follower in profile.get_followers():
                followers.append({
                    "username": follower.username,
                    "full_name": follower.full_name,
                    "profile_pic_url": follower.profile_pic_url,
                    "is_private": follower.is_private,
                    "is_verified": follower.is_verified
                })
                count += 1
                if count % 50 == 0:
                    console.print(f"[yellow]Retrieved {count} followers...[/yellow]")
            
            with open(f"{output_dir}/followers.json", "w") as f:
                json.dump({
                    "timestamp": timestamp,
                    "count": len(followers),
                    "followers": followers
                }, f, indent=4)
            console.print(f"[green]Followers saved to {output_dir}/followers.json[/green]")
            
            # Get following
            console.print("[yellow]Downloading following list (this may take time)...[/yellow]")
            following = []
            count = 0
            
            for followee in profile.get_followees():
                following.append({
                    "username": followee.username,
                    "full_name": followee.full_name,
                    "profile_pic_url": followee.profile_pic_url,
                    "is_private": followee.is_private,
                    "is_verified": followee.is_verified
                })
                count += 1
                if count % 50 == 0:
                    console.print(f"[yellow]Retrieved {count} following...[/yellow]")
            
            with open(f"{output_dir}/following.json", "w") as f:
                json.dump({
                    "timestamp": timestamp,
                    "count": len(following),
                    "following": following
                }, f, indent=4)
            console.print(f"[green]Following saved to {output_dir}/following.json[/green]")
            
            # Get recent posts (limited to 12 to avoid rate limiting)
            console.print("[yellow]Downloading recent posts data...[/yellow]")
            posts = []
            count = 0
            
            for post in profile.get_posts():
                if count >= 12:  # Limit to recent 12 posts
                    break
                    
                posts.append({
                    "shortcode": post.shortcode,
                    "url": f"https://www.instagram.com/p/{post.shortcode}/",
                    "date": str(post.date_utc),
                    "caption": post.caption,
                    "likes": post.likes,
                    "comments": post.comments,
                    "type": "video" if post.is_video else "image"
                })
                count += 1
            
            with open(f"{output_dir}/recent_posts.json", "w") as f:
                json.dump({
                    "timestamp": timestamp,
                    "count": len(posts),
                    "posts": posts
                }, f, indent=4)
            console.print(f"[green]Recent posts saved to {output_dir}/recent_posts.json[/green]")
        else:
            console.print("[yellow]This is a private account. Can only save public information.[/yellow]")
            
        console.print("[bold green]Data export completed successfully![/bold green]")
        console.print(f"[bold blue]All data saved in the '{output_dir}' folder[/bold blue]")
        
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # For backwards compatibility if script is called without arguments
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    main()
