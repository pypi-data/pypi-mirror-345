# CDP Chrome Tabs

A Python package for interacting with Chrome tabs via the Chrome DevTools Protocol.

## Installation

```bash
pip install cdp-chrome-tabs
```

Or install from source:

```bash
git clone https://github.com/guocity/cdp-chrome-tabs.git
cd cdp-chrome-tabs
pip install -e .
```

## Prerequisites

For this package to work, Chrome must be running with remote debugging enabled. You can start Chrome with:

```bash
# On macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

# On Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

# On Linux
google-chrome --remote-debugging-port=9222
```

## Usage

```python
from cdp_chrome_tabs import ChromeTabs


# one line print active tab
print(f"Active Tab URL: {ChromeTabs().get_active_tab().url if ChromeTabs().get_active_tab() else 'No active tab'}")

# Get all tabs
tabs = chrome.get_all_tabs()
for tab in tabs:
    print(f"Tab ID: {tab.id}")
    print(f"Title: {tab.title}")
    print(f"URL: {tab.url}")
    print("---")

# Get the active tab
active_tab = chrome.get_active_tab()
if active_tab:
    print(f"Active tab: {active_tab.title} - {active_tab.url}")

# Find a tab by ID
tab = chrome.get_tab_by_id("some-tab-id")

# Find a tab by URL (exact match)
tab = chrome.get_tab_by_url("https://www.example.com")

# Find a tab by URL (partial match)
tab = chrome.get_tab_by_url("example.com", partial_match=True)
```

## License

MIT
