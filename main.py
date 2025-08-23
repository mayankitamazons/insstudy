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
            
    def login(self, force_new=False):
        """Handle login to Instagram with improved error handling"""
        self.console.print("[bold blue]Starting Instagram login...[/bold blue]")
        
        # Session file path
        session_file = f"{os.path.expanduser('~')}/.instaloader_session"
        
        # Remove session if forcing a new login
        if force_new and os.path.exists(session_file):
            try:
                os.remove(session_file)
                self.console.print("[yellow]Forced new login: removed old session file[/yellow]")
            except Exception:
                pass
        
        # Try to use existing session first (if not forcing new)
        if not force_new and os.path.exists(session_file):
            try:
                self.console.print("[yellow]Trying to use existing session...[/yellow]")
                self.insta.load_session_from_file(None, session_file)
                self.console.print("[green]Loaded existing session successfully![/green]")
                return True
            except Exception as e:
                self.console.print(f"[yellow]Could not use existing session: {e}[/yellow]")
                self.console.print("[yellow]Will try browser-based login...[/yellow]")
        
        # Try browser-based login
        try:
            self.console.print("[yellow]Opening web browser for Instagram login...[/yellow]")
            self.console.print("[bold yellow]IMPORTANT: Make sure to complete login in the browser including any security checks![/bold yellow]")
            self.insta.interactive_login(None)  # Will open browser
            self.console.print("[green]Login successful![/green]")
            
            # Test the session with a simple request
            try:
                self.console.print("[yellow]Testing Instagram session...[/yellow]")
                test_profile = instaloader.Profile.from_username(self.insta.context, "instagram")
                self.console.print(f"[green]Session test successful (verified {test_profile.username})![/green]")
            except Exception as test_error:
                self.console.print(f"[bold red]Session test failed: {test_error}[/bold red]")
                self.console.print("[yellow]Instagram may be asking for additional verification.[/yellow]")
                self.console.print("[yellow]Try checking the browser window for any challenges.[/yellow]")
                return False
            
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
        """Manual login via username/password with improved guidance"""
        self.console.print("[yellow]Trying manual login...[/yellow]")
        self.console.print("[bold yellow]IMPORTANT: Instagram might block programmatic logins.[/bold yellow]")
        self.console.print("[yellow]It's strongly recommended to use a dedicated Instagram account for scraping.[/yellow]")
        self.console.print("[yellow]If you're using your main account, consider creating a secondary account instead.[/yellow]")
        
        try:
            username = input("Instagram username: ")
            from getpass import getpass
            password = getpass("Instagram password (input will be hidden): ")
            
            self.console.print("[yellow]Attempting to log in...[/yellow]")
            self.insta.login(username, password)
            
            # Test the session with a simple request
            try:
                self.console.print("[yellow]Testing Instagram session...[/yellow]")
                test_profile = instaloader.Profile.from_username(self.insta.context, "instagram")
                self.console.print(f"[green]Login successful! Session test verified.[/green]")
            except Exception as test_error:
                self.console.print(f"[bold red]Session test failed: {test_error}[/bold red]")
                self.console.print("[yellow]Instagram may be asking for additional verification.[/yellow]")
                return False
                
            # Save session for future use
            try:
                session_file = f"{os.path.expanduser('~')}/.instaloader_session"
                self.insta.save_session_to_file(session_file)
                self.console.print("[yellow]Session saved for future use[/yellow]")
            except Exception:
                pass
                
            return True
        except instaloader.exceptions.BadCredentialsException:
            self.console.print("[bold red]Login failed: Invalid username or password[/bold red]")
            return False
        except instaloader.exceptions.TwoFactorAuthRequiredException:
            self.console.print("[bold red]Login failed: Two-factor authentication is enabled[/bold red]")
            self.console.print("[yellow]Use browser-based login instead to handle 2FA[/yellow]")
            return False
        except instaloader.exceptions.ConnectionException as e:
            self.console.print(f"[bold red]Login failed: Connection error - {e}[/bold red]")
            self.console.print("[yellow]Instagram may be rate-limiting your requests or blocking your IP[/yellow]")
            return False
        except Exception as e:
            self.console.print(f"[bold red]Manual login failed: {e}[/bold red]")
            return False
    
    def get_followers(self, max_retries=3):
        """Get followers for the specified username with robust error handling"""
        retry_count = 0
        wait_time = 30  # Start with 30 seconds wait
        
        while retry_count <= max_retries:
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
                
                # For large accounts, warn about potential issues
                if followers_count > 1000:
                    self.console.print("[bold yellow]⚠️ This account has many followers. Instagram may rate-limit the requests.[/bold yellow]")
                    self.console.print("[bold yellow]⚠️ We'll try to handle this by using delays between requests.[/bold yellow]")
                
                # Prepare data structures
                followers = []
                count = 0
                
                # Collect followers data with rate limiting awareness
                with self.console.status("[bold green]Downloading followers list...") as status:
                    # Get follower iterator
                    follower_iterator = profile.get_followers()
                    
                    # Process followers with built-in delays to avoid rate limiting
                    for follower in follower_iterator:
                        followers.append({
                            "username": follower.username,
                            "full_name": follower.full_name,
                            "profile_pic_url": follower.profile_pic_url,
                            "is_private": follower.is_private,
                            "is_verified": follower.is_verified
                        })
                        
                        count += 1
                        
                        # Add small delays to avoid rate limiting
                        if count % 10 == 0:
                            time.sleep(0.5)  # 500ms delay every 10 followers
                        
                        if count % 50 == 0:
                            self.console.print(f"[yellow]Retrieved {count} followers so far...[/yellow]")
                            time.sleep(1.5)  # Longer delay every 50 followers
                        
                        # For larger batches, take a break to avoid triggering rate limits
                        if count % 200 == 0:
                            self.console.print(f"[yellow]Taking a short break to avoid rate limits (retrieved {count} so far)...[/yellow]")
                            time.sleep(5)  # 5 second pause every 200 followers
                
                # Return collected data
                self.console.print(f"[bold green]Successfully collected {len(followers)} followers![/bold green]")
                return {
                    "timestamp": str(datetime.datetime.now()),
                    "username": self.username,
                    "followers_count": followers_count,
                    "followers": followers
                }
                
            except instaloader.exceptions.ConnectionException as e:
                error_message = str(e).lower()
                
                # Check for rate limiting or unauthorized errors
                if "401" in error_message or "unauthorized" in error_message or "wait" in error_message:
                    retry_count += 1
                    
                    if retry_count <= max_retries:
                        self.console.print(f"[bold yellow]Instagram is rate limiting requests. Waiting for {wait_time} seconds before retry {retry_count}/{max_retries}...[/bold yellow]")
                        self.console.print(f"[yellow]Error details: {e}[/yellow]")
                        time.sleep(wait_time)
                        wait_time *= 2  # Exponential backoff
                        
                        # Try to refresh session
                        self.console.print("[yellow]Attempting to refresh session...[/yellow]")
                        try:
                            # Re-login if needed
                            self.login()
                        except Exception as login_error:
                            self.console.print(f"[yellow]Session refresh failed: {login_error}[/yellow]")
                    else:
                        self.console.print("[bold red]Maximum retries reached. Instagram is blocking requests.[/bold red]")
                        self.console.print("[yellow]Tips to resolve:[/yellow]")
                        self.console.print("[yellow]1. Try again later (wait at least 30 minutes)[/yellow]")
                        self.console.print("[yellow]2. Use a different Instagram account to log in[/yellow]")
                        self.console.print("[yellow]3. Try from a different network (Instagram may block IPs)[/yellow]")
                        raise
                else:
                    # For other connection errors
                    self.console.print(f"[bold red]Connection error: {e}[/bold red]")
                    raise
                    
            except Exception as e:
                self.console.print(f"[bold red]Error fetching followers: {str(e)}[/bold red]")
                return None
                
        # If we've exhausted all retries
        self.console.print("[bold red]All retry attempts failed. Could not retrieve followers.[/bold red]")
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
    
    def run(self, force_login=False):
        """Main execution flow with improved error handling"""
        # Show anti-rate limiting tips
        self.console.print("\n[bold blue]===== Instagram API Rate Limiting Tips =====[/bold blue]")
        self.console.print("[yellow]1. Instagram strictly limits automated access to their API[/yellow]")
        self.console.print("[yellow]2. For accounts with many followers, data may be incomplete[/yellow]")
        self.console.print("[yellow]3. If you encounter 401 errors, wait 30+ minutes before retrying[/yellow]")
        self.console.print("[yellow]4. Using a VPN might help if your IP is being rate-limited[/yellow]")
        self.console.print("[yellow]5. Consider using a dedicated Instagram account for scraping[/yellow]")
        self.console.print("[bold blue]===========================================[/bold blue]\n")
        
        # Attempt login
        if not self.login(force_new=force_login):
            self.console.print("[bold red]Login failed. Cannot continue.[/bold red]")
            self.console.print("[yellow]Try using the --force-login option if you keep seeing this error[/yellow]")
            return False
        
        try:
            # Get followers data with built-in retry mechanism
            self.console.print("[yellow]Starting data collection (this might take a while for larger accounts)...[/yellow]")
            followers_data = self.get_followers(max_retries=3)
            
            # Save to JSON
            if followers_data:
                saved = self.save_to_json(followers_data)
                if saved:
                    self.console.print("\n[bold green]✅ Data collection completed successfully![/bold green]")
                    return True
            
            self.console.print("[bold red]Failed to collect or save followers data.[/bold red]")
            return False
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Data collection interrupted by user.[/yellow]")
            return False
        except Exception as e:
            self.console.print(f"[bold red]Error during data collection: {str(e)}[/bold red]")
            return False


def main():
    # Parse command line arguments
    parser = ArgumentParser(
        prog="Instagram Followers Exporter",
        description="Export Instagram followers list to JSON",
    )
    parser.add_argument("-u", "--username", help="Instagram username to fetch followers from", required=True)
    parser.add_argument("-o", "--output", help="Output JSON filename (default: USERNAME_followers.json)")
    parser.add_argument("--force-login", action="store_true", help="Force a new login session, ignoring cached credentials")
    parser.add_argument("--max-retries", type=int, default=3, help="Maximum number of retries for rate-limited requests")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")
    
    args = parser.parse_args()
    
    # Initialize and run
    console = Console()
    console.print("[bold blue]Instagram Followers Exporter v1.0.0[/bold blue]")
    console.print("[yellow]This tool exports Instagram followers data to JSON format[/yellow]")
    
    # Show warning about Instagram's policies
    console.print("\n[bold red]⚠️ DISCLAIMER ⚠️[/bold red]")
    console.print("[yellow]Instagram's Terms of Service restrict automated data collection.[/yellow]")
    console.print("[yellow]Use this tool responsibly and at your own risk.[/yellow]")
    console.print("[yellow]Excessive use may result in your account being temporarily blocked.[/yellow]\n")
    
    exporter = InstaFollowers(args.username)
    success = exporter.run(force_login=args.force_login)
    
    # Save to specified output file if provided
    if success and args.output:
        try:
            with open(f"{args.username}_followers.json", 'r') as f:
                followers_data = json.load(f)
            exporter.save_to_json(followers_data, args.output)
        except Exception as e:
            console.print(f"[bold red]Error saving to custom output file: {e}[/bold red]")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"Unexpected error: {e}")
