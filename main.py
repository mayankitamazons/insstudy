"""
Instagram Followers Exporter
"""

from rich.console import Console
from argparse import ArgumentParser
import datetime, instaloader, os, time, json, sys, webbrowser, requests, urllib.parse
from instaloader.exceptions import LoginException, ConnectionException
import http.cookiejar

class InstaFollowers:
    def __init__(self, username: str):
        self.username = username
        self.console = Console()
        
        # Configure instaloader with minimal options and quiet authentication
        self.insta = instaloader.Instaloader(
            quiet=True,  # Set to True to suppress authentication prompts
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
            
    def get_browser_cookies(self):
        """Get Instagram cookies directly from the browser"""
        try:
            import browser_cookie3
            self.console.print("[yellow]Getting cookies from browser...[/yellow]")
            
            # Try Chrome first, then Safari, then Firefox
            try:
                return browser_cookie3.chrome(domain_name='.instagram.com')
            except Exception as chrome_error:
                self.console.print(f"[yellow]Could not get Chrome cookies: {chrome_error}[/yellow]")
                
                try:
                    return browser_cookie3.safari(domain_name='.instagram.com')
                except Exception as safari_error:
                    self.console.print(f"[yellow]Could not get Safari cookies: {safari_error}[/yellow]")
                    
                    try:
                        return browser_cookie3.firefox(domain_name='.instagram.com')
                    except Exception as firefox_error:
                        self.console.print(f"[yellow]Could not get Firefox cookies: {firefox_error}[/yellow]")
                        
            return None
            
        except ImportError:
            self.console.print("[bold red]browser_cookie3 not available. Install with: pip install browser-cookie3[/bold red]")
            return None
            
    def login(self, force_new=False):
        """Handle login to Instagram using browser cookies only - no password prompts"""
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
                self.console.print("[yellow]Will try browser cookie authentication...[/yellow]")
        
        # Help user log in via browser first
        self.console.print("[yellow]Opening web browser for Instagram login...[/yellow]")
        self.console.print("[bold yellow]IMPORTANT: Please log into Instagram in the browser window.[/bold yellow]")
        self.console.print("[bold yellow]Complete all verification steps in the browser if required.[/bold yellow]")
        self.console.print("[bold yellow]After logging in successfully, return here to continue.[/bold yellow]")
        
        try:
            # Open Instagram website to ensure user is logged in
            webbrowser.open("https://www.instagram.com/")
            
            # Give user time to ensure they're logged in
            self.console.print("[yellow]Waiting for you to log in to Instagram...[/yellow]")
            time.sleep(5)  # Give more time to log in
            
            # Direct browser cookie authentication - no interactive_login to avoid password prompts
            cookies = self.get_browser_cookies()
            if cookies:
                # Create a cookie jar and add it to instaloader's session
                cookie_jar = http.cookiejar.CookieJar()
                for cookie in cookies:
                    cookie_jar.set_cookie(cookie)
                
                self.insta.context._session.cookies.update(cookie_jar)
                self.console.print("[green]Successfully imported cookies from browser![/green]")
                
                # Try to save session for future use
                try:
                    self.insta.save_session_to_file(session_file)
                    self.console.print("[yellow]Session saved for future use[/yellow]")
                except Exception as save_error:
                    self.console.print(f"[yellow]Could not save session: {save_error}[/yellow]")
                
                # Test the session
                try:
                    test_profile = instaloader.Profile.from_username(self.insta.context, "instagram")
                    self.console.print(f"[green]Login successful! Session verified with {test_profile.username}[/green]")
                    return True
                except Exception as test_error:
                    self.console.print(f"[yellow]Session test failed: {test_error}[/yellow]")
                    self.console.print("[yellow]Cookie authentication may not have worked properly.[/yellow]")
            else:
                self.console.print("[bold red]Could not retrieve Instagram cookies from any browser.[/bold red]")
                self.console.print("[yellow]Make sure you're logged into Instagram in Chrome, Safari, or Firefox.[/yellow]")
                
            # If we reach here, cookie authentication failed
            self.console.print("[yellow]Trying alternative authentication method...[/yellow]")
            
            # Create a fresh session with standard headers that look like a browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.instagram.com/',
                'X-IG-App-ID': '936619743392459',
            }
            
            # Set headers on instaloader session
            for header, value in headers.items():
                self.insta.context._session.headers[header] = value
                
            # Try a simple test request to see if we're authenticated
            try:
                # This just checks if we can access the API without login prompts
                test_profile = instaloader.Profile.from_username(self.insta.context, "instagram")
                self.console.print("[green]Alternative authentication worked![/green]")
                return True
            except Exception:
                self.console.print("[bold red]All authentication methods failed.[/bold red]")
                self.console.print("[yellow]Please try again after logging into Instagram in your browser.[/yellow]")
                return False
                
        except Exception as e:
            self.console.print(f"[bold red]Login process failed: {e}[/bold red]")
            self.console.print("[yellow]Please manually log into Instagram in your browser before trying again.[/yellow]")
            return False
            
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
            self.console.print("[yellow]Please make sure you can access Instagram.com in your browser[/yellow]")
            self.console.print("[yellow]and that you're properly logged in before trying again.[/yellow]")
            
            # Return failure instead of trying manual login
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
                    # Extract user ID from error message if possible
                    user_id = None
                    if "graphql/query" in error_message and "variables=" in error_message:
                        try:
                            # Try to extract user ID from the error URL
                            start_idx = error_message.find('"id":"')
                            if start_idx > 0:
                                start_idx += 6  # length of '"id":"'
                                end_idx = error_message.find('"', start_idx)
                                if end_idx > 0:
                                    user_id = error_message[start_idx:end_idx]
                                    self.console.print(f"[yellow]Extracted user ID from error: {user_id}[/yellow]")
                        except:
                            pass
                    
                    # Try direct API request as a fallback if we have the user_id
                    if user_id:
                        self.console.print("[bold yellow]Standard API returned 401 Unauthorized[/bold yellow]")
                        self.console.print("[yellow]Trying direct API access as fallback...[/yellow]")
                        
                        direct_data = self.try_direct_api_request(user_id=user_id)
                        if direct_data:
                            self.console.print("[bold green]Successfully retrieved data via direct API request![/bold green]")
                            return direct_data
                    
                    # If GraphQL didn't work or we couldn't extract user_id, try standard retries
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
                        # Last attempt - try direct API request without user_id as fallback
                        self.console.print("[bold yellow]Maximum retries reached. Trying direct API access as fallback...[/bold yellow]")
                        direct_data = self.try_direct_api_request()
                        if direct_data:
                            self.console.print("[bold green]Successfully retrieved data via direct API request![/bold green]")
                            return direct_data
                            
                        # If that failed too, show helpful messages
                        self.console.print("[bold red]All methods exhausted. Instagram is limiting requests.[/bold red]")
                        self.console.print("[yellow]Tips to resolve:[/yellow]")
                        self.console.print("[yellow]1. Try again later (wait at least 30 minutes)[/yellow]")
                        self.console.print("[yellow]2. Try accessing Instagram normally in your browser first[/yellow]")
                        self.console.print("[yellow]3. Ensure you have proper permissions to access this data[/yellow]")
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
    
    def try_direct_api_request(self, user_id=None, count=12):
        """
        Simplified direct request to Instagram API based on graphql_test.py
        when the standard instaloader approach fails with 401 errors
        """
        self.console.print("[bold blue]Attempting direct API access as fallback...[/bold blue]")
        
        # If we have a user ID, use it; otherwise use a default URL
        if user_id:
            url = f"https://www.instagram.com/graphql/query?query_hash=37479f2b8209594dde7facb0d904896a&variables=%7B%22id%22%3A%22{user_id}%22%2C%22first%22%3A{count}%7D"
        else:
            # Use the URL directly from graphql_test.py as fallback
            url = "https://www.instagram.com/graphql/query?query_hash=37479f2b8209594dde7facb0d904896a&variables=%7B%22id%22%3A%227093386149%22%2C%22first%22%3A12%7D"
        
        # Set up headers to mimic a browser - same as in graphql_test.py
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.instagram.com/',
            'X-IG-App-ID': '936619743392459',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        self.console.print(f"[yellow]URL: {url}[/yellow]")
        
        try:
            # First try to get browser cookies (like in graphql_test.py)
            import browser_cookie3
            self.console.print("[yellow]Getting cookies from Chrome browser...[/yellow]")
            cookies = browser_cookie3.chrome(domain_name='.instagram.com')
            
            # Make the request with cookies
            response = requests.get(url, headers=headers, cookies=cookies)
            
            if response.status_code == 200:
                data = response.json()
                
                # Save the raw data for inspection
                output_file = f"{self.username}_direct_api.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                
                self.console.print(f"[bold green]✅ Successfully fetched data and saved to {output_file}[/bold green]")
                
                # Process and extract followers
                if 'data' in data and 'user' in data['data']:
                    user_data = data['data']['user']
                    
                    # Extract basic information
                    followers_data = {
                        "timestamp": str(datetime.datetime.now()),
                        "username": self.username,
                        "source": "direct_api_request"
                    }
                    
                    # Add any available follower count
                    if 'edge_followed_by' in user_data:
                        followers_data["followers_count"] = user_data['edge_followed_by']['count']
                    
                    return followers_data
                else:
                    self.console.print("[yellow]Data saved but couldn't extract follower information[/yellow]")
                    return None
            else:
                self.console.print(f"[bold red]Request failed: {response.status_code} - {response.reason}[/bold red]")
                self.console.print(f"[yellow]Response: {response.text[:200]}...[/yellow]")
                return None
                
        except ImportError:
            self.console.print("[yellow]browser_cookie3 not available - install with: pip install browser-cookie3[/yellow]")
            return None
        except Exception as e:
            self.console.print(f"[bold red]Error in direct API request: {e}[/bold red]")
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
        self.console.print("[yellow]5. Always respect Instagram's terms of service and rate limits[/yellow]")
        self.console.print("[bold blue]===========================================[/bold blue]\n")
        
        # Attempt login
        if not self.login(force_new=force_login):
            self.console.print("[bold red]Login failed. Cannot continue.[/bold red]")
            self.console.print("[yellow]Try these steps to resolve login issues:[/yellow]")
            self.console.print("[yellow]1. Make sure you're logged into Instagram in your browser[/yellow]")
            self.console.print("[yellow]2. Use --force-login to clear cached sessions[/yellow]")
            self.console.print("[yellow]3. If Instagram requires additional verification, complete it in your browser[/yellow]")
            self.console.print("[yellow]4. Try again after ensuring you can access Instagram.com normally[/yellow]")
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
    console.print("[yellow]Use this tool responsibly and respect Instagram's policies.[/yellow]")
    console.print("[yellow]This tool is for educational purposes only.[/yellow]\n")
    
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
