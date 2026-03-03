import asyncio
from playwright.async_api import async_playwright
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
from urllib.parse import urljoin
import threading

# Modern color palette
COLORS = {
    "bg_dark": "#0f0f12",
    "bg_card": "#18181f",
    "bg_input": "#252530",
    "border": "#2d2d3a",
    "text": "#e4e4e7",
    "text_muted": "#71717a",
    "accent": "#06b6d4",
    "accent_hover": "#22d3ee",
    "success": "#22c55e",
    "error": "#ef4444",
    "warning": "#f59e0b",
}


class BrokenLinkElementFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Broken Link & Element Finder")
        self.root.geometry("820x580")
        self.root.minsize(640, 480)
        self.root.configure(bg=COLORS["bg_dark"])

        self._setup_styles()
        self._build_ui()
        self.xpath_baseline = []

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Card.TFrame",
            background=COLORS["bg_card"],
        )
        style.configure(
            "Card.TLabel",
            background=COLORS["bg_card"],
            foreground=COLORS["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Title.TLabel",
            background=COLORS["bg_dark"],
            foreground=COLORS["text"],
            font=("Segoe UI", 24, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background=COLORS["bg_dark"],
            foreground=COLORS["text_muted"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "Accent.TButton",
            font=("Segoe UI", 11, "bold"),
            padding=(24, 12),
            background=COLORS["accent"],
            foreground=COLORS["bg_dark"],
        )
        style.map(
            "Accent.TButton",
            background=[("active", COLORS["accent_hover"]), ("pressed", COLORS["accent_hover"])],
        )

    def _build_ui(self):
        # Main container with padding
        main = tk.Frame(self.root, bg=COLORS["bg_dark"], padx=24, pady=24)
        main.pack(fill=tk.BOTH, expand=True)

        # Header
        header = tk.Frame(main, bg=COLORS["bg_dark"])
        header.pack(fill=tk.X, pady=(0, 20))
        ttk.Label(header, text="Broken Link & Element Finder", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(
            header,
            text="Scan a URL for broken links and unresponsive clickable elements.",
            style="Subtitle.TLabel",
        ).pack(anchor=tk.W)

        # Card: URL input
        card = ttk.Frame(main, style="Card.TFrame", padding=20)
        card.pack(fill=tk.X, pady=(0, 16))
        card.configure(borderwidth=0)

        inner = tk.Frame(card, bg=COLORS["bg_card"])
        inner.pack(fill=tk.X)
        ttk.Label(inner, text="URL to scan", style="Card.TLabel").pack(anchor=tk.W, pady=(0, 8))
        self.url_entry = tk.Entry(
            inner,
            font=("Segoe UI", 11),
            bg=COLORS["bg_input"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            highlightthickness=2,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
        )
        self.url_entry.pack(fill=tk.X, ipady=10, ipadx=12, pady=(0, 16))
        self.url_entry.bind("<FocusIn>", lambda e: self.url_entry.configure(highlightbackground=COLORS["accent"]))
        self.url_entry.bind("<FocusOut>", lambda e: self.url_entry.configure(highlightbackground=COLORS["border"]))

        btn_frame = tk.Frame(inner, bg=COLORS["bg_card"])
        btn_frame.pack(fill=tk.X)
        self.start_btn = ttk.Button(
            btn_frame,
            text="Start Scan",
            style="Accent.TButton",
            command=self.start_scan_thread,
        )
        self.start_btn.pack(anchor=tk.W)

        # Log section
        log_header = tk.Frame(main, bg=COLORS["bg_dark"])
        log_header.pack(fill=tk.X, pady=(8, 6))
        ttk.Label(log_header, text="Output", style="Subtitle.TLabel").pack(anchor=tk.W)

        log_card = tk.Frame(main, bg=COLORS["bg_card"], highlightthickness=1, highlightbackground=COLORS["border"])
        log_card.pack(fill=tk.BOTH, expand=True, pady=(0, 0))

        self.log_area = scrolledtext.ScrolledText(
            log_card,
            font=("Consolas", 10),
            bg=COLORS["bg_input"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief=tk.FLAT,
            padx=16,
            pady=16,
        )
        self.log_area.pack(fill=tk.BOTH, expand=True)
        self.log_area.configure(selectbackground=COLORS["accent"], selectforeground=COLORS["bg_dark"])

        # Tag colors for log
        self.log_area.tag_configure("info", foreground=COLORS["text"])
        self.log_area.tag_configure("broken", foreground=COLORS["error"])
        self.log_area.tag_configure("ok", foreground=COLORS["success"])
        self.log_area.tag_configure("muted", foreground=COLORS["text_muted"])

    def log(self, message, tag="info"):
        self.log_area.insert(tk.END, message + "\n", tag)
        self.log_area.see(tk.END)
        print(message)

    def start_scan_thread(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL.")
            return
        self.start_btn.config(state=tk.DISABLED)
        self.log_area.delete("1.0", tk.END)
        self.log(f"Starting scan for: {url}", "muted")
        threading.Thread(target=self.run_scan, args=(url,), daemon=True).start()

    def run_scan(self, url):
        asyncio.run(self.scan(url))
        self.start_btn.config(state=tk.NORMAL)

    async def scan(self, url):
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url)
                self.log("Page loaded successfully.", "ok")

                # Collect and test all links
                anchors = await page.query_selector_all("a[href]")
                links = []
                for a in anchors:
                    href = await a.get_attribute("href")
                    if href:
                        full_url = urljoin(url, href)
                        if any(full_url.startswith(scheme) for scheme in ["mailto:", "tel:", "javascript:", "#"]):
                            continue
                        links.append(full_url)

                self.log(f"Found {len(links)} links.", "info")

                broken_links = 0
                for link in links:
                    try:
                        response = await page.request.get(link, timeout=5000)
                        status = response.status
                        if status >= 400:
                            self.log(f"[Broken Link] {link} - Status: {status}", "broken")
                            broken_links += 1
                    except Exception as e:
                        self.log(f"[Broken Link] {link} - Request Failed: {e}", "broken")
                        broken_links += 1

                # Test clickable elements with detailed info
                clickable_elements = await page.query_selector_all(
                    "button, [role=button], a[href], input[type='button'], input[type='submit'], input[type='reset'], .btn, .clickable"
                )
                self.log(f"Found {len(clickable_elements)} clickable elements.", "info")

                unresponsive_count = 0

                for i, el in enumerate(clickable_elements, start=1):
                    try:
                        tag_name = await el.evaluate("(el) => el.tagName.toLowerCase()")
                        text = await el.evaluate("(el) => el.innerText || el.textContent || ''")
                        text = text.strip()
                        element_id = await el.get_attribute("id") or ""
                        element_class = await el.get_attribute("class") or ""
                        aria_label = await el.get_attribute("aria-label") or ""

                        description = f"<{tag_name}>"
                        if text:
                            description += f" Text='{text}'"
                        if element_id:
                            description += f" id='{element_id}'"
                        if element_class:
                            description += f" class='{element_class}'"
                        if aria_label:
                            description += f" aria-label='{aria_label}'"

                        await el.click(timeout=5000)
                        self.log(f"[Responsive] Element {i} clicked successfully: {description}", "ok")

                    except Exception as e:
                        self.log(f"[Unresponsive] Element {i} ({description}) - {e}", "broken")
                        unresponsive_count += 1

                self.log("Scan complete.", "ok")
                self.log(f"Broken links found: {broken_links}", "broken" if broken_links else "info")
                self.log(f"Unresponsive elements found: {unresponsive_count}", "broken" if unresponsive_count else "info")
                self.log(f"XPath changes detected: 0  (feature not implemented)", "muted")

                await browser.close()

        except Exception as e:
            self.log(f"Error during scan: {e}", "broken")

if __name__ == "__main__":
    root = tk.Tk()
    app = BrokenLinkElementFinderApp(root)
    root.mainloop()
