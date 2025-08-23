"""
Instagram Followers Exporter
"""

from rich.console import Console
from argparse import ArgumentParser
import datetime, instaloader, os, time, json, sys, webbrowser
from instaloader.exceptions import LoginException, ConnectionException

class InstaFollowers:
    def __init__(self, username: str):
        self.username = username
        self.console = Console()
        
        # Configure instaloader with minimal options
        self.insta = instaloader.Instaloader(
            quiet=False,
            download_pictures=False,
            download_videos=False, 
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            max_connection_attempts=3
        )
    
    @property
    def date(self):
        try:
            return datetime.datetime.now(datetime.UTC)
        except AttributeError:
            return datetime.datetime.now(datetime.timezone.utc)
            
    def login(self):
        """Handle login to Instagram"""
        self.console.print("[bold blue]Starting Instagram login...[/bold blue]")
        
        # Clear any existing sessions
        session_file = f"{os.path.expanduser('~')}/.instaloader_session"
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
                self.console.print("[yellow]Removed old session file[/yellow]")
            except Exception:
                pass
        
        # Try browser-based login
        try:
            self.console.print("[yellow]Opening web browser for Instagram login...[/yellow]")
            self.insta.interactive_login(None)  # Will open browser
            self.console.print("[green]Login successful![/green]")
            
            # Save session for future use
            try:
                self.insta.save_session_to_file(session_file)
                self.console.print("[yellow]Session saved for future use[/yellow]")
            except Exception:
                pass
                
            return True
        except Exception as e:
            self.console.print(f"[bold red]Browser login failed: {e}[/bold red]")
            
            # Try manual login as fallback
            return self.manual_login()
    
    def manual_login(self):
        """Manual login via username/password"""
        self.console.print("[yellow]Trying manual login...[/yellow]")
        
        try:
            username = input("Instagram username: ")
            from getpass import getpass
            password = getpass("Instagram password (input will be hidden): ")
            
            self.insta.login(username, password)
            self.console.print("[green]Login successful![/green]")
            return True
        except Exception as e:
            self.console.print(f"[bold red]Manual login failed: {e}[/bold red]")
            return False
    
    def get_followers(self):
        """Get followers for the specified username"""
        try:
            self.console.print(f"[bold blue]Fetching followers for {self.username}...[/bold blue]")
            
            # Get profile
            profile = instaloader.Profile.from_username(self.insta.context, self.username)
            
            # Check if profile exists
            if not profile:
                self.console.print(f"[bold red]Profile '{self.username}' not found![/bold red]")
                return None
                
            # Check if profile is private
            if profile.is_private and profile.username != self.insta.context.username:
                self.console.print("[bold red]This profile is private and you're not following it![/bold red]")
                return None
            
            # Get followers count
            followers_count = profile.followers
            self.console.print(f"[yellow]This account has {followers_count} followers. Collecting data...[/yellow]")
            
            # Prepare data structures
            followers = []
            count = 0
            
            # Collect followers data
            with self.console.status("[bold green]Downloading followers list...") as status:
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
                        self.console.print(f"[yellow]Retrieved {count} followers so far...[/yellow]")
            
            # Return collected data
            self.console.print(f"[bold green]Successfully collected {len(followers)} followers![/bold green]")
            return {
                "timestamp": str(datetime.datetime.now()),
                "username": self.username,
                "followers_count": followers_count,
                "followers": followers
            }
            
        except Exception as e:
            self.console.print(f"[bold red]Error fetching followers: {str(e)}[/bold red]")
            return None
    
    def save_to_json(self, data, filename=None):
        """Save followers data to JSON file"""
        if not data:
            self.console.print("[bold red]No data to save![/bold red]")
            return False
        
        if filename is None:
            filename = f"{self.username}_followers.json"
            
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            self.console.print(f"[bold green]Data saved to {filename}![/bold green]")
            return True
        except Exception as e:
            self.console.print(f"[bold red]Error saving data: {str(e)}[/bold red]")
            return False
    
    def run(self):
        """Main execution flow"""
        # Attempt login
        if not self.login():
            self.console.print("[bold red]Login failed. Cannot continue.[/bold red]")
            return False
        
        # Get followers data
        followers_data = self.get_followers()
        
        # Save to JSON
        if followers_data:
            self.save_to_json(followers_data)
            return True
        else:
            return False


def main():
    # Parse command line arguments
    parser = ArgumentParser(
        prog="Instagram Followers Exporter",
        description="Export Instagram followers list to JSON",
    )
    parser.add_argument("-u", "--username", help="Instagram username to fetch followers from", required=True)
    parser.add_argument("-o", "--output", help="Output JSON filename (default: USERNAME_followers.json)")
    
    args = parser.parse_args()
    
    # Initialize and run
    exporter = InstaFollowers(args.username)
    success = exporter.run()
    
    # Save to specified output file if provided
    if success and args.output:
        with open(f"{args.username}_followers.json", 'r') as f:
            followers_data = json.load(f)
        exporter.save_to_json(followers_data, args.output)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
