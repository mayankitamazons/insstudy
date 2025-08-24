<br/>
<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/2048px-Instagram_logo_2016.svg.png" alt="Logo" width="20%" height="20%">
  
  <h2 align="center">Instagram Followers Exporter</h3>

  <p align="center">
    📸 A tool to export Instagram followers data to JSON format
    <br />
    <br />
  </p>
</div>

---------------------------------------

## Features

- Export followers data for any public Instagram account
- Supports JSON export with detailed follower information
- Web-based authentication with session caching
- Smart rate-limit handling with automatic retries
- Command-line interface with various options

```
python3 main.py -h
usage: Instagram Followers Exporter [-h] -u USERNAME [-o OUTPUT] [--force-login]
                                   [--max-retries MAX_RETRIES] [--version]

Export Instagram followers list to JSON

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Instagram username to fetch followers from
  -o OUTPUT, --output OUTPUT
                        Output JSON filename (default: USERNAME_followers.json)
  --force-login         Force a new login session, ignoring cached credentials
  --max-retries MAX_RETRIES
                        Maximum number of retries for rate-limited requests
  --version             show program's version number and exit
```
## Important Notes

> [!IMPORTANT]
> You must login to *your* Instagram account in order to properly access follower data. This is due to Instagram blocking `HTTPS GET` requests from unauthenticated sessions. This tool uses browser-based authentication only - you must be logged into Instagram in your browser.

> [!CAUTION]
> Instagram's Terms of Service restrict automated data collection. Use this tool responsibly and respect Instagram's policies. This tool is for educational purposes only.

> [!TIP]
> Always respect rate limits and pause between requests to avoid temporary restrictions.

## Installation

> [!TIP]
> [Install Python 3.7+ if you don't have it already](https://www.python.org/downloads/)

#### Install from this repository:

```bash
# Clone the repository (or download the ZIP file)
$ git clone https://github.com/yourusername/instagram-followers-exporter.git
$ cd instagram-followers-exporter

# Install dependencies
$ pip install -r requirements.txt
```

## Usage

```bash
# Basic usage - export followers for an account
$ python main.py -u instagram

# Specify a custom output filename
$ python main.py -u instagram -o custom_filename.json

# Force a new login session (useful if you're having auth issues)
$ python main.py -u instagram --force-login

# Adjust retry attempts for rate limiting
$ python main.py -u instagram --max-retries 5
```

## Output Format

The tool exports followers data to a JSON file with the following structure:

```json
{
  "timestamp": "2023-07-15 12:34:56.789012",
  "username": "instagram",
  "followers_count": 123,
  "followers": [
    {
      "username": "follower1",
      "full_name": "Follower One",
      "profile_pic_url": "https://...",
      "is_private": false,
      "is_verified": true
    },
    ...
  ]
}
```

## Handling Rate Limits

Instagram strictly rate-limits API access. This tool implements several strategies to work within these limits:

1. Progressive delays between requests
2. Exponential backoff for retry attempts 
3. Session testing to detect authentication issues
4. Detailed error messages with guidance

If you encounter rate limiting issues:
- Wait at least 30 minutes before trying again
- Try using a different network connection
- Make sure you're properly logged into Instagram in your browser

## Troubleshooting

### Common Issues and Solutions

#### Login Problems
- If login fails, try using `--force-login` to clear cached sessions
- Make sure to complete all verification steps in the browser window
- For private accounts, you must be following the account to access their data

#### 401 Unauthorized Errors
- This usually indicates Instagram rate limiting
- Wait at least 30 minutes before trying again
- Consider using a different network connection

#### Incomplete Data
- For accounts with large follower counts, Instagram may not return complete data
- The script implements progressive delays to avoid triggering rate limits
- Try collecting data during off-peak hours

## Built With
- [Python](https://www.python.org/) - Programming language
- [Instaloader](https://github.com/instaloader/instaloader) - Instagram scraping library
- [Rich](https://github.com/Textualize/rich) - Terminal formatting library

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions to improve the tool are welcome! Here are some ways you can contribute:

- Report bugs and issues
- Add new features or improve existing ones
- Improve documentation
- Suggest optimizations for handling Instagram's rate limiting

Please follow these steps to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Disclaimer

This tool is provided for educational purposes only. Use it responsibly and in accordance with Instagram's Terms of Service. The developers are not responsible for any misuse of this tool or for any restrictions applied to your Instagram account as a result of using this tool.
### Create a New Branch
Before making any changes, it's recommended to create a new branch. This ensures that your changes won't interfere with other contributions and keeps the main branch clean. Use the following command to create and switch to a new branch:
```bash
$ git checkout -b branch-name
```
### Make the Desired Changes
Now, you can proceed to make your desired changes to the project. Whether it's fixing bugs, adding new features, improving documentation, or optimising code, your efforts will be instrumental in enhancing the project.

### Commit and Push Changes
Once you have made the necessary changes, commit your work using the following commands:
```bash
$ git add .
$ git commit -m "Your commit message"
```
Push the changes to your forked repository:
```bash
$ git push origin branch-name
```
### Submit a Pull Request
Head over to the [original repository](https://github.com/ibnaleem/instatracker) on GitHub and go to the ["Pull requests"](https://github.com/ibnaleem/instatracker/pulls) tab.
1. Click on the "New pull request" button.
2. Select your forked repository and the branch containing your changes.
3. Provide a clear and informative title for your pull request, and use the description box to explain the modifications you have made. **_Your pull request will be closed if you do not specify the changes you've made._**
4. Finally, click on the "Create pull request" button to submit your changes.

## [PGP Fingerprint](https://github.com/ibnaleem/ibnaleem/blob/main/public_key.asc)
```
2024 7EC0 23F2 769E 6618  1C0F 581B 4A2A 862B BADE
```
![GitHub Opensource](https://img.shields.io/badge/open%20source-yes-orange) ![GitHub Maintained](https://img.shields.io/badge/maintained-yes-yellow) ![Last Commit](https://img.shields.io/github/last-commit/ibnaleem/instatracker) ![Commit Activity](https://img.shields.io/github/commit-activity/w/ibnaleem/instatracker) ![Issues](https://img.shields.io/github/issues/ibnaleem/instatracker) ![Forks](https://img.shields.io/github/forks/ibnaleem/instatracker)
