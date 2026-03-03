# LinkBroken

**Broken Link & Element Finder** — A desktop tool that scans any webpage for broken links and unresponsive clickable elements. Built for QA, site audits, and keeping your sites link-healthy.

---

## Features

- **Broken link detection** — Crawls all `<a href>` links on the page and reports 4xx/5xx responses or failed requests
- **Clickable element testing** — Finds buttons, links, and interactive elements and tests each for responsiveness (timeout/errors reported)
- **Modern dark UI** — Clean interface with color-coded output (errors in red, success in green)
- **Headless browser** — Uses Playwright (Chromium) for accurate, real-page behavior
- **Skip non-HTTP links** — Ignores `mailto:`, `tel:`, `javascript:`, and fragment-only (`#`) links

---

## Requirements

- **Python 3.8+**
- **Playwright** (Chromium browser)

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/andrewaminazm/linkbroken.git
   cd linkbroken
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install playwright
   playwright install chromium
   ```

---

## Usage

1. Run the application:

   ```bash
   python linkbroken.py
   ```

2. Enter the full URL to scan (e.g. `https://example.com`) in the input field.

3. Click **Start Scan**. The tool will:
   - Load the page
   - Collect and check all HTTP(S) links
   - Find and click buttons, links, and other clickables
   - Stream results in the output area with color-coded messages

4. Review the log: broken links and unresponsive elements are highlighted in red; successful checks in green.

---

## Tech Stack

- **Python** — Application logic
- **Tkinter** — Desktop GUI (ttk for themed widgets)
- **Playwright** — Headless browser automation and network checks

---

## License

MIT
