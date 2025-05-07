from typing import Any, List, Dict
import click
import smtplib
import ssl
import logging
import textwrap
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum
import imaplib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("email-mcp")

@click.command()
@click.option(
    "--smtp-server",
    envvar="SMTP_SERVER",
    required=True,
    help="SMTP server address",
)
@click.option(
    "--smtp-username",
    envvar="SMTP_USERNAME",
    required=True,
    help="SMTP username",
)
@click.option(
    "--smtp-password",
    envvar="SMTP_PASSWORD",
    required=True,
    help="SMTP password",
)
@click.option(
    "--imap-server",
    envvar="IMAP_SERVER",
    required=True,
    help="IMAP server address",
)
@click.option(
    "--imap-username",
    envvar="IMAP_USERNAME",
    required=True,
    help="IMAP username",
)
@click.option(
    "--imap-password",
    envvar="IMAP_PASSWORD",
    required=True,
    help="IMAP password",
)
def main(
    smtp_server: str,
    smtp_username: str,
    smtp_password: str,
    imap_server: str,
    imap_username: str,
    imap_password: str
):
    # Pydantic models for tool and prompt definitions
    class ToolDefinition(BaseModel):
        """Definition of an MCP tool with name and description."""
        name: str
        description: str

    # Constants
    class Config:
        """Configuration constants for the Email MCP server."""
        SMTP_PORT = 587
        IMAP_PORT = 993
        TIMEOUT = 30

    class Tool(Enum):
        """Enumeration of MCP tool definitions."""
        SEND_EMAIL = ToolDefinition(
            name="send_email",
            description=textwrap.dedent("""
                Send an email using SMTP.
                
                Parameters:
                - to_email (string, required): The recipient's email address. Example: "recipient@example.com"
                - subject (string, required): The subject line of the email. Example: "Meeting Reminder"
                - body (string, required): The content of the email message. Can be plain text.
                - cc (string, optional): List of email addresses to CC. Example: "cc1@example.com, cc2@example.com"
                
                Returns:
                - Confirmation message if the email was sent successfully
                - Error message if the email failed to send
                
                Example usage:
                - Send a simple email: to_email="john@example.com", subject="Hello", body="This is a test email" (MUST be in HTML format)
                - Send with CC: to_email="john@example.com", subject="Meeting", body="Please join" (MUST be in HTML format), cc="team@example.com, team2@example.com"
            """).strip()
        )
        SEARCH_MAILBOX = ToolDefinition(
            name="search_mailbox",
            description=textwrap.dedent("""
                Search emails in a mailbox using IMAP.
                
                Parameters:
                - search_criteria (list of strings, required): The search criteria for the emails. See detailed options below.
                - folder (string, optional): The mailbox folder to search in. Default is "INBOX".
                - limit (integer, optional): Maximum number of results to return. Default is 1.
                
                Available search criteria:
                
                Basic Search:
                - ALL - return all messages
                - NEW - match new messages
                - OLD - match old messages
                - RECENT - match messages with the \\RECENT flag set
                
                Message Status:
                - ANSWERED - match messages with the \\ANSWERED flag set
                - DELETED - match deleted messages
                - FLAGGED - match messages with the \\FLAGGED flag set
                - SEEN - match messages that have been read
                - UNANSWERED - match messages that have not been answered
                - UNDELETED - match messages that are not deleted
                - UNFLAGGED - match messages that are not flagged
                - UNSEEN - match messages which have not been read yet
                
                Header Fields:
                - BCC "string" - match messages with "string" in the Bcc: field
                - CC "string" - match messages with "string" in the Cc: field
                - FROM "string" - match messages with "string" in the From: field
                - SUBJECT "string" - match messages with "string" in the Subject:
                - TO "string" - match messages with "string" in the To:
                
                Content Search:
                - BODY "string" - match messages with "string" in the body
                - TEXT "string" - match messages with text "string"
                
                Date Search:
                - BEFORE "date" - match messages with Date: before "date"
                - ON "date" - match messages with Date: matching "date"
                - SINCE "date" - match messages with Date: after "date"
                
                Keywords:
                - KEYWORD "string" - match messages with "string" as a keyword
                - UNKEYWORD "string" - match messages that do not have the keyword "string"
            """).strip()
        )

    # Error handling
    class EmailError(Exception):
        """Exception raised for errors in email operations."""
        def __init__(self, message: str):
            self.message = message
            super().__init__(self.message)

    # Service layer
    class EmailService:
        """Service for managing email operations."""
        def __init__(self, smtp_server: str, smtp_username: str, smtp_password: str,
                    imap_server: str, imap_username: str, imap_password: str):
            self.smtp_server = smtp_server
            self.smtp_username = smtp_username
            self.smtp_password = smtp_password
            self.imap_server = imap_server
            self.imap_username = imap_username
            self.imap_password = imap_password

        def send_email(
            self, 
            to_email: str,
            subject: str,
            body: str,
            cc: str,
        ) -> Dict[str, str]:
            """Send an email using SMTP."""
            try:
                # Create message
                msg = MIMEMultipart()
                msg['From'] = self.smtp_username
                msg['To'] = ','.join(to_email.split(','))
                msg['Subject'] = subject

                if cc:
                    msg['Cc'] = ','.join(cc.split(','))
                
                msg.attach(MIMEText(body, 'html'))

                client=smtplib.SMTP(
                    host=self.smtp_server,
                    port=587
                )
                client.starttls()
                client.login(
                    user=self.smtp_username,
                    password=self.smtp_password
                )
                client.send_message(
                    from_addr=self.smtp_username,
                    to_addrs=to_email,
                    msg=msg
                )
                client.quit()

                return {"status": "success", "message": f"Email sent successfully, cc: {cc}, to: {to_email}, subject: {subject}, body: {body}, msg: {msg.as_string()}"}
                
            except Exception as e:
                logger.error(f"Error sending email: {str(e)}")
                raise EmailError(f"Failed to send email: {str(e)}")
            
        def search_mailbox(
            self,
            search_criteria: list,
            folder: str = "INBOX",
            limit: int = 1
        ) -> List[Dict[str, Any]]:
            """Search emails in a mailbox using IMAP."""
            
            try:
                # Connect to IMAP server with timeout
                client=imaplib.IMAP4_SSL(host=self.imap_server)

                try:
                    # Login to server
                    client.login(self.imap_username, self.imap_password)
                    # Select folder
                    client.select(folder)
                    
                    # Search for emails
                    _, ids = client.search(None, *search_criteria)
                    ids=str(ids[0].decode('utf-8')).split(' ')
                    
                    # Limit results
                    messages = ids[:limit]
                    
                    # Fetch email data
                    results = []
                    for msg_id in messages:
                        _, msg_data = client.fetch(msg_id, '(RFC822)')
                        email_body = msg_data[0][1].decode('utf-8')
                        
                        # Extract email details
                        result = {
                            "email": email_body
                        }
                        results.append(result)
                    
                    return results
                
                except ssl.SSLError as e:
                    raise EmailError(f"SSL error connecting to IMAP server: {str(e)}")
                except Exception as e:
                    raise EmailError(f"Error accessing mailbox: {str(e)}")
                finally:
                    # Ensure connection is closed
                    try:
                        client.logout()
                    except:
                        pass
                    
            except Exception as e:
                logger.error(f"Error searching mailbox: {str(e)}")
                raise EmailError(f"Failed to search mailbox: {str(e)}")

    # Global service instance
    email_service = None

    email_service = EmailService(
        smtp_server=smtp_server,
        smtp_username=smtp_username,
        smtp_password=smtp_password,
        imap_server=imap_server,
        imap_username=imap_username,
        imap_password=imap_password
    )

    mcp = FastMCP("email")

    # Tool implementations
    @mcp.tool(
            name=Tool.SEND_EMAIL.value.name,
            description=Tool.SEND_EMAIL.value.description
        )
    def send_email(
        to_email: str = Field(..., description="The recipient's email addresses. Example: 'recipient@example.com, recipient2@example.com'"),
        subject: str = Field(..., description="The subject line of the email. Example: 'Meeting Reminder'"),
        body: str = Field(..., description="The content of the email message. MUST be in HTML format."),
        cc: str = Field(default="", description="List of email addresses to CC. Example: 'cc1@example.com, cc2@example.com'"),
    ) -> List[Dict[str, str]]:
        """Send an email using SMTP."""
        try:
            result = email_service.send_email(
                to_email=to_email,
                subject=subject,
                body=body,
                cc=cc,
            )
            return [{"type": "text", "text": result["message"]}]
        except EmailError as e:
            return [{"type": "text", "text": f"Error: {e.message}"}]
        except Exception as e:
            logger.exception("Unexpected error in send_email")
            return [{"type": "text", "text": f"Error sending email: {str(e)}"}]

    @mcp.tool(
            name=Tool.SEARCH_MAILBOX.value.name,
            description=Tool.SEARCH_MAILBOX.value.description
        )
    def search_mailbox(
        search_criteria: list = Field(..., description=textwrap.dedent("""
            The search criteria for the emails in a list of strings. Available options:
            
            Basic Search:
            - ALL - return all messages
            - NEW - match new messages
            - OLD - match old messages
            - RECENT - match messages with the \\RECENT flag set
            
            Message Status:
            - ANSWERED - match messages with the \\ANSWERED flag set
            - DELETED - match deleted messages
            - FLAGGED - match messages with the \\FLAGGED flag set
            - SEEN - match messages that have been read
            - UNANSWERED - match messages that have not been answered
            - UNDELETED - match messages that are not deleted
            - UNFLAGGED - match messages that are not flagged
            - UNSEEN - match messages which have not been read yet
            
            Header Fields:
            - BCC "string" - match messages with "string" in the Bcc: field
            - CC "string" - match messages with "string" in the Cc: field
            - FROM "string" - match messages with "string" in the From: field
            - SUBJECT "string" - match messages with "string" in the Subject:
            - TO "string" - match messages with "string" in the To:
            
            Content Search:
            - BODY "string" - match messages with "string" in the body
            - TEXT "string" - match messages with text "string"
            
            Date Search:
            - BEFORE "date" - match messages with Date: before "date"
            - ON "date" - match messages with Date: matching "date"
            - SINCE "date" - match messages with Date: after "date"
            
            Keywords:
            - KEYWORD "string" - match messages with "string" as a keyword
            - UNKEYWORD "string" - match messages that do not have the keyword "string"
            
            EXAMPLE:
            - ["SUBJECT", "some subject"]
            - ["FROM", "john@example.com"]
            - ["SINCE", "01-Jan-2024"]
            - ["UNSEEN"]
            - ["FLAGGED"]
            - ["TEXT", "some text"]
        """).strip()),
        folder: str = Field("INBOX", description="The mailbox folder to search in. Default is 'INBOX'"),
        limit: int = Field(1, description="Maximum number of results to return. Default is 1")
    ) -> List[Dict[str, str]]:
        """Search emails in a mailbox using IMAP."""
        try:
            results = email_service.search_mailbox(
                search_criteria=search_criteria,
                folder=folder,
                limit=limit
            )
            
            if not results:
                return [{"type": "text", "text": "No emails found matching the search criteria"}]
            
            return results
        except EmailError as e:
            return [{"type": "text", "text": f"Error: {e.message}"}]
        except Exception as e:
            logger.exception("Unexpected error in search_mailbox")
            return [{"type": "text", "text": f"Error searching mailbox: {str(e)}"}]
    
    logger.info("Starting Email MCP server")
        
    # Run the MCP server
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main() 