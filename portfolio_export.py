"""Export a Yahoo Finance portfolio to CSV.

Uses a persistent Playwright browser session so you only log in once;
cookies live in .yahoo_session/ and are reused on later runs.

Usage:
    python portfolio_export.py                     # default: p_4 portfolio
    python portfolio_export.py -u <portfolio_url>  # a different portfolio
    python portfolio_export.py --no-enrich         # skip yfinance lookups
"""
import argparse
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

SESSION_DIR = Path(__file__).parent / ".yahoo_session"
DEFAULT_URL = "https://finance.yahoo.com/portfolio/p_4/view/v1"
LOGIN_HOSTS = ("login.yahoo.com", "guce.yahoo.com", "consent.yahoo.com")
NAV_TIMEOUT_MS = 60000
LOGIN_TIMEOUT_S = 600
TABLE_SELECTOR = "table tbody tr"


def log(msg: str) -> None:
    print(f"[portfolio_export {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a Yahoo Finance portfolio to CSV.")
    parser.add_argument("-u", "--url", default=DEFAULT_URL, help="Portfolio URL to export.")
    parser.add_argument("-o", "--output", default=None, help="Output CSV path (default: portfolio_<id>_<timestamp>.csv).")
    parser.add_argument("--headless", action="store_true", help="Run the browser headless (session must already be logged in).")
    parser.add_argument("--no-enrich", action="store_true", help="Skip yfinance company-name enrichment.")
    return parser.parse_args()


def is_login_url(url: str) -> bool:
    return any(host in url.lower() for host in LOGIN_HOSTS)


def fetch_rows(page) -> list[dict]:
    """Wait for navigation/login, then read the holdings table into dicts."""
    log(f"navigating to {page.url}")
    deadline = time.monotonic() + LOGIN_TIMEOUT_S
    while True:
        if is_login_url(page.url):
            log("on Yahoo login page -- please sign in in the browser window...")
        try:
            page.wait_for_selector(TABLE_SELECTOR, timeout=3000, state="attached")
            log("holdings table found")
            break
        except Exception:
            if time.monotonic() > deadline:
                raise TimeoutError(f"Timed out waiting for holdings table ({LOGIN_TIMEOUT_S}s).")
            page.wait_for_timeout(1000)

    return parse_tables(page)


def parse_tables(page) -> list[dict]:
    tables = page.query_selector_all("table")
    for table in tables:
        header_cells = table.query_selector_all("thead th")
        if not header_cells:
            header_cells = table.query_selector_all("tr:first-child th, tr:first-child td")
        if not header_cells:
            continue

        headers = []
        for h in header_cells:
            text = (h.inner_text() or "").strip()
            headers.append(re.sub(r"\s+", " ", text))

        symbol_col = None
        for i, h in enumerate(headers):
            if "symbol" in h.lower():
                symbol_col = i
                break
        if symbol_col is None:
            continue

        body_rows = table.query_selector_all("tbody tr")
        if not body_rows:
            body_rows = table.query_selector_all("tr")[1:]

        rows = []
        for row in body_rows:
            cells = row.query_selector_all("td")
            if len(cells) <= symbol_col:
                continue
            symbol_cell = cells[symbol_col]
            symbol = extract_symbol_from_cell(symbol_cell)
            if not symbol:
                continue
            values = [(c.inner_text() or "").strip() for c in cells]
            values[symbol_col] = symbol
            rows.append({headers[i]: v for i, v in enumerate(values) if i < len(headers)})
        if rows:
            return rows
    return []


def extract_symbol_from_cell(cell) -> str:
    try:
        link = cell.query_selector('a[href*="/quote/"]')
        if link:
            href = link.get_attribute("href") or ""
            m = re.search(r"/quote/([^?/&]+)", href)
            if m:
                return m.group(1)
    except Exception:
        pass
    return extract_symbol(cell.inner_text() or "")


def extract_symbol(text: str) -> str:
    m = re.match(r"[A-Z][A-Z0-9.\-^]*", text)
    return m.group(0) if m else ""


def enrich_company_names(rows: list[dict]) -> None:
    if not rows:
        return
    symbols = []
    seen = set()
    for row in rows:
        s = row.get("symbol", row.get("Symbol", ""))
        if s and s not in seen:
            seen.add(s)
            symbols.append(s)
    try:
        import yfinance as yf
    except ImportError:
        log("yfinance not installed; skipping company-name enrichment")
        return

    log(f"enriching {len(symbols)} symbol(s) with company names...")
    names: dict[str, str] = {}

    def fetch(sym: str) -> tuple[str, str]:
        try:
            info = yf.Ticker(sym).info
            return sym, info.get("shortName") or info.get("longName") or ""
        except Exception:
            return sym, ""

    with ThreadPoolExecutor(max_workers=6) as ex:
        for sym, name in ex.map(fetch, symbols):
            names[sym] = name

    for row in rows:
        s = row.get("symbol", row.get("Symbol", ""))
        row["Company Name"] = names.get(s, "")


def write_csv(rows: list[dict], output: Path) -> None:
    import csv

    all_keys: list[str] = []
    for row in rows:
        for k in row:
            if k not in all_keys:
                all_keys.append(k)

    symbol_headers = [k for k in all_keys if "symbol" in k.lower()]
    non_symbol = [k for k in all_keys if k not in symbol_headers]
    if "Company Name" in non_symbol:
        non_symbol.remove("Company Name")
    order = symbol_headers + non_symbol + (["Company Name"] if any("Company Name" in r for r in rows) else [])

    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=order)
        writer.writeheader()
        writer.writerows(rows)
    log(f"wrote {len(rows)} row(s) to {output}")


def capture_api_responses(context, api_files: list[Path]) -> None:
    def on_response(response) -> None:
        url = response.url
        if any(k in url for k in ("/ws/", "/v7/finance/desktop/portfolio", "portfolio/")) \
                and "download" not in url:
            try:
                body = response.text()
            except Exception:
                return
            if body and body.lstrip().startswith(("{", "[")):
                stamp = time.strftime("%Y%m%d-%H%M%S")
                fname = SESSION_DIR / f"portfolio_api_{stamp}_{len(api_files)}.json"
                fname.write_text(body, encoding="utf-8")
                api_files.append(fname)
                log(f"captured portfolio API response -> {fname}")
    try:
        context.on("response", on_response)
    except Exception:
        pass


def main() -> None:
    args = parse_args()
    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    output = args.output
    if not output:
        m = re.search(r"/p_(\d+)", args.url)
        pf_id = m.group(1) if m else "portfolio"
        output = f"portfolio_p{int(pf_id)}_{datetime.now():%Y%m%d_%H%M%S}.csv"
    output = Path(output)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=args.headless,
            viewport={"width": 1280, "height": 900},
        )
        api_files: list[Path] = []
        capture_api_responses(context, api_files)

        page = context.new_page()
        try:
            page.goto(args.url, wait_until="domcontentloaded", timeout=NAV_TIMEOUT_MS)
            rows = fetch_rows(page)
        finally:
            page.close()
            context.close()

    if not rows:
        sys.exit("No holdings table found on the page. Did you sign in / are you on the right portfolio?")

    if not args.no_enrich:
        enrich_company_names(rows)
    write_csv(rows, output)
    print(f"\nDone. Open {output}")


if __name__ == "__main__":
    main()