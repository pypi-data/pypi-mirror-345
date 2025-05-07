# Email MCP server

[![smithery badge](https://smithery.ai/badge/@mhazarabad/email-mcp)](https://smithery.ai/server/@mhazarabad/email-mcp)

## Overview

A Model Context Protocol server for managing email operations using SMTP and IMAP. This server provides tools to send emails and search mailboxes programmatically.

## Prerequisites

- SMTP server credentials (server address, username, password)
- IMAP server credentials (server address, username, password)
- For Gmail users:
  - Enable 2-Factor Authentication
  - Generate an App Password from Google Account settings
  - Use the App Password instead of your regular password

## Installation

### Installing via Smithery

To install email-mcp for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@mhazarabad/email-mcp):

```bash
npx -y @smithery/cli install @mhazarabad/email-mcp --client claude
```

The package is not published to PyPI. You'll need to clone this repository and run it directly from source.

```bash
git clone https://github.com/mhazarabad/email-mcp.git
cd email-mcp
```


## Running the Server

### Using Gmail (Recommended)

For Gmail accounts, use the following command format:

```bash
python -m email_mcp \
  --smtp-server "smtp.gmail.com" \
  --smtp-username "your-email@gmail.com" \
  --smtp-password "your-app-password" \
  --imap-server "imap.gmail.com" \
  --imap-username "your-email@gmail.com" \
  --imap-password "your-app-password"
```


### Using Other Email Providers

Replace the server addresses and credentials according to your email provider:

```bash
python -m email_mcp \
  --smtp-server "your-smtp-server" \
  --smtp-username "your-email" \
  --smtp-password "your-password" \
  --imap-server "your-imap-server" \
  --imap-username "your-email" \
  --imap-password "your-password"
```

Common Email Provider Settings:
- Outlook:
  - SMTP: smtp.office365.com
  - IMAP: outlook.office365.com
- Yahoo:
  - SMTP: smtp.mail.yahoo.com
  - IMAP: imap.mail.yahoo.com

## Tools

1. `send_email`
   - Send an email using SMTP
   - Input:
     - `to_email` (string, required): Recipient email addresses (comma-separated). Example: "recipient@example.com, recipient2@example.com"
     - `subject` (string, required): Email subject line. Example: "Meeting Reminder"
     - `body` (string, required): Email content in HTML format
     - `cc` (string, optional): CC recipient email addresses (comma-separated). Example: "cc1@example.com, cc2@example.com"
   - Returns: Confirmation of email being sent

2. `search_mailbox`
   - Search emails in a mailbox using IMAP
   - Input:
     - `search_criteria` (list of strings, required): IMAP search criteria
     - `folder` (string, optional): Mailbox folder to search (default: "INBOX")
     - `limit` (integer, optional): Maximum number of results (default: 10)
   - Returns: List of matching emails with their details

### Search Criteria Examples

The `search_criteria` parameter supports various IMAP search options:

Basic Search:
- `["ALL"]` - Return all messages
- `["NEW"]` - Match new messages
- `["UNSEEN"]` - Match unread messages

Message Status:
- `["ANSWERED"]` - Match answered messages
- `["FLAGGED"]` - Match flagged messages
- `["SEEN"]` - Match read messages

Header Fields:
- `["FROM", "sender@example.com"]` - Match sender
- `["SUBJECT", "Meeting"]` - Match subject
- `["TO", "recipient@example.com"]` - Match recipient

Content Search:
- `["BODY", "keyword"]` - Search in message body
- `["TEXT", "keyword"]` - Search in all message text

Date Search:
- `["SINCE", "01-Jan-2024"]` - Match messages after date
- `["BEFORE", "01-Jan-2024"]` - Match messages before date
- `["ON", "01-Jan-2024"]` - Match messages on date

## Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
"mcpServers": {
  "email": {
    "command": "python",
    "args": [
      "-m",
      "email_mcp",
      "--smtp-server",
      "smtp.gmail.com",
      "--smtp-username",
      "your-email@gmail.com",
      "--smtp-password",
      "your-app-password",
      "--imap-server",
      "imap.gmail.com",
      "--imap-username",
      "your-email@gmail.com",
      "--imap-password",
      "your-app-password"
    ]
  }
}
```

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
