"""
Module for interacting with Chrome tabs via the Chrome DevTools Protocol.
"""

import logging
import requests
from typing import List, Dict, Optional, Any

# Configure logger
logger = logging.getLogger(__name__)

class ChromeTab:
    """Represents a Chrome browser tab."""
    
    def __init__(self, tab_data: Dict[str, Any]):
        """
        Initialize a ChromeTab object.
        
        Args:
            tab_data: Dictionary containing tab information from CDP
        """
        self.id = tab_data.get("id")
        self.url = tab_data.get("url")
        self.title = tab_data.get("title")
        self.type = tab_data.get("type")
        self.websocket_debugger_url = tab_data.get("webSocketDebuggerUrl")
        self.dev_tools_frontend_url = tab_data.get("devtoolsFrontendUrl")
        self.raw_data = tab_data
        self.is_local_host = bool(self.url and 'localhost' in self.url)
        self.new_tab = (self.url == 'chrome://newtab')
    
    def __repr__(self) -> str:
        return f"ChromeTab(id={self.id}, title={self.title}, url={self.url})"


class ChromeTabs:
    """Manages interactions with Chrome tabs via Chrome DevTools Protocol."""
    
    def __init__(self, cdp_url: str = "http://localhost:9222"):
        """
        Initialize the ChromeTabs manager.
        
        Args:
            cdp_url: URL of the Chrome DevTools Protocol endpoint
                    Default is http://localhost:9222
        """
        self.cdp_url = cdp_url
        try:
            response = requests.get(f"{self.cdp_url}/json")
            response.raise_for_status()
            tabs_data = response.json()
            self._tabs = [ChromeTab(tab) for tab in tabs_data if tab.get("type")=="page" and not tab.get("url",""
                ).startswith("chrome-extension:")]
        except requests.RequestException as e:
            logger.error(f"Failed to fetch tabs during init: {e}")
            self._tabs = []
    
    def get_all_tabs(self) -> List[ChromeTab]:
        """
        Get a list of all Chrome tabs.
        
        Returns:
            List of ChromeTab objects representing all tabs
            
        Raises:
            requests.RequestException: If there's an error connecting to Chrome
        """
        return self._tabs
    
    def get_active_tab(self) -> Optional[ChromeTab]:
        """
        Get the currently active Chrome tab.
        
        Returns:
            ChromeTab object representing the active tab, or None if no active tab is found
            
        Raises:
            requests.RequestException: If there's an error connecting to Chrome
        """
        try:
            tabs = self.get_all_tabs()
            
            # The first tab in the list is typically the active one
            return tabs[0] if tabs else None
        except requests.RequestException as e:
            logger.error(f"Failed to connect to Chrome: {e}")
            return None
    
    def get_tab_by_id(self, tab_id: str) -> Optional[ChromeTab]:
        """
        Get a tab by its ID.
        
        Args:
            tab_id: The ID of the tab to find
            
        Returns:
            ChromeTab object with the specified ID, or None if not found
        """
        tabs = self.get_all_tabs()
        return next((tab for tab in tabs if tab.id == tab_id), None)
    
    def get_tab_by_url(self, url: str, partial_match: bool = False) -> Optional[ChromeTab]:
        """
        Get a tab by its URL.
        
        Args:
            url: The URL to search for
            partial_match: If True, finds tabs whose URLs contain the specified string
                          If False, requires an exact match
            
        Returns:
            First matching ChromeTab object, or None if not found
        """
        tabs = self.get_all_tabs()
        
        if partial_match:
            return next((tab for tab in tabs if url in tab.url), None)
        else:
            return next((tab for tab in tabs if tab.url == url), None)
