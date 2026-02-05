"""
GitHub Integration for Support Tickets
"""
import os
import logging
from typing import Dict, Any, Optional, List
from github import Github, GithubException, Auth

from config import GITHUB_TOKEN, GITHUB_REPO


class GitHubSupport:
    """Handles GitHub issue creation for support tickets"""
    
    def __init__(self, token: Optional[str] = None, repo_name: Optional[str] = None, folder: Optional[str] = None):
        self.token = token or GITHUB_TOKEN
        self.repo_name = repo_name or GITHUB_REPO
        self.folder = folder or os.getenv("GITHUB_FOLDER", "")
        self.logger = logging.getLogger(__name__)
        
        self.github = None
        self.repo = None
        
        if self.token and self.repo_name:
            try:
                # Use Auth.Token for authentication
                auth = Auth.Token(self.token)
                self.github = Github(auth=auth)
                self.repo = self.github.get_repo(self.repo_name)
                self.logger.info(f"GitHub integration initialized for repo: {self.repo_name}")
            except Exception as e:
                self.logger.warning(f"GitHub initialization failed: {e}")
    
    def is_configured(self) -> bool:
        """Check if GitHub integration is properly configured"""
        return self.github is not None and self.repo is not None
    
    def _ensure_label_exists(self, label_name: str, color: str = "0075ca"):
        """Ensures a label exists in the repository, creates it if it doesn't"""
        if not self.repo:
            return
        try:
            self.repo.get_label(label_name)
        except GithubException:
            try:
                self.repo.create_label(name=label_name, color=color)
                self.logger.info(f"Created new label: {label_name}")
            except Exception as e:
                self.logger.warning(f"Could not create label {label_name}: {e}")

    def create_issue(
        self, 
        title: str, 
        body: str, 
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a GitHub issue as a support ticket
        
        Args:
            title: Issue title
            body: Issue description
            labels: Optional list of labels to add
            
        Returns:
            Dictionary with success status and issue details
        """
        if not self.is_configured():
            self.logger.warning("GitHub not configured, using mock mode")
            return self._create_mock_ticket(title, body, labels)
        
        try:
            issue_labels = []
            
            # 1. Handle folder label and title decoration
            if self.folder:
                folder_label = self.folder.lower().replace("/", "-").replace(" ", "-")
                self._ensure_label_exists(folder_label, "0075ca") # Blue
                issue_labels.append(folder_label)
                
                # Decorate title
                prefixed_title = f"[{self.folder}] {title}"
                # Add details to body
                full_body = f"**Project:** {self.folder}\n\n**Description:**\n{body}"
            else:
                prefixed_title = title
                full_body = body

            # 2. Add customer-support label (ensure it exists)
            self._ensure_label_exists("customer-support", "d73a4a") # Reddish
            issue_labels.append("customer-support")

            # 3. Add any additional labels provided
            if labels:
                for label in labels:
                    if label not in issue_labels:
                        # Ensure these labels exist too
                        self._ensure_label_exists(label, "e6e6e6") # Light gray
                        issue_labels.append(label)
            
            # Create the issue
            issue = self.repo.create_issue(
                title=prefixed_title,
                body=full_body,
                labels=issue_labels
            )
            
            self.logger.info(f"Created GitHub issue #{issue.number}: {prefixed_title}")
            
            return {
                "success": True,
                "message": f"Ticket created successfully! Ticket ID: #{issue.number}",
                "issue_number": issue.number,
                "issue_url": issue.html_url,
                "title": prefixed_title
            }
            
        except GithubException as e:
            # Handle Validation Failed with more detail
            error_data = getattr(e, 'data', {})
            error_msg = error_data.get('message', str(e))
            errors = error_data.get('errors', [])
            
            full_error = f"GitHub API error: {error_msg}"
            if errors:
                full_error += f" - Details: {str(errors)}"
                
            self.logger.error(full_error)
            return {
                "success": False,
                "error": full_error
            }
        except Exception as e:
            error_msg = f"Error creating issue: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
        except Exception as e:
            error_msg = f"Error creating issue: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def _create_mock_ticket(
        self, 
        title: str, 
        body: str, 
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Create a mock support ticket when GitHub is not configured"""
        import random
        
        mock_id = f"MOCK-{random.randint(1000, 9999)}"
        
        self.logger.info(f"Created mock support ticket: {mock_id}")
        
        return {
            "success": True,
            "message": "Support ticket created (Mock Mode - GitHub not configured)",
            "ticket_id": mock_id,
            "title": title,
            "labels": labels or [],
            "note": "To enable real GitHub integration, set GITHUB_TOKEN and GITHUB_REPO in your .env file"
        }
