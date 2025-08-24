#!/usr/bin/env python3
"""
Quick test script for GraphQL API access
"""

import requests
import json
import sys
from rich.console import Console

console = Console()

def main():
    # The URL from the user's request
    url = "https://www.instagram.com/graphql/query?query_hash=37479f2b8209594dde7facb0d904896a&variables=%7B%22id%22%3A%227093386149%22%2C%22first%22%3A12%7D"
    
    # Set up headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.instagram.com/',
        'X-IG-App-ID': '936619743392459',
        'X-Requested-With': 'XMLHttpRequest',
    }
    
    console.print("[bold blue]Testing direct access to Instagram GraphQL API...[/bold blue]")
    console.print(f"[yellow]URL: {url}[/yellow]")
    
    try:
        # Try without cookies first
        console.print("[yellow]Attempting to fetch data without authentication...[/yellow]")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            # Save the data
            with open('instagram_graphql_direct.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            console.print("[bold green]✅ Successfully fetched and saved data to instagram_graphql_direct.json[/bold green]")
            return
        else:
            console.print(f"[yellow]Request without auth failed: {response.status_code} - {response.reason}[/yellow]")
            
        # Try with browser cookies
        try:
            import browser_cookie3
            console.print("[yellow]Trying with browser cookies...[/yellow]")
            cookies = browser_cookie3.chrome(domain_name='.instagram.com')
            
            response = requests.get(url, headers=headers, cookies=cookies)
            
            if response.status_code == 200:
                data = response.json()
                # Save the data
                with open('instagram_graphql_with_cookies.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                console.print("[bold green]✅ Successfully fetched and saved data to instagram_graphql_with_cookies.json[/bold green]")
            else:
                console.print(f"[bold red]Request with cookies failed: {response.status_code} - {response.reason}[/bold red]")
                console.print(f"[yellow]Response: {response.text[:200]}...[/yellow]")
        except ImportError:
            console.print("[yellow]browser_cookie3 not available - install with: pip install browser-cookie3[/yellow]")
        except Exception as e:
            console.print(f"[bold red]Error retrieving cookies: {e}[/bold red]")
        
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")

if __name__ == "__main__":
    main()
