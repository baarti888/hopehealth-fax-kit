import pandas as pd
import asyncio
from playwright.async_api import async_playwright

async def main():
    # Load your CSV file (make sure doctors_faxplus_upload.csv is in the same folder)
    df = pd.read_csv("doctors_faxplus_upload.csv")

    # Find all name columns (anything with "name" in the header)
    name_cols = [c for c in df.columns if "name" in c.lower()]
    names = []
    for c in name_cols:
        names += df[c].dropna().astype(str).tolist()

    # Keep unique names only (up to first 10 for testing)
    names = list(dict.fromkeys(names))[:10]

    # Launch Chromium
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        for name in names:
            page = await context.new_page()

            # Load your HTML template
            with open("fax_template.html", "r", encoding="utf-8") as f:
                html = f.read().replace("{{Name}}", name)

            # Set the HTML content and wait for all assets to load
            await page.set_content(html, wait_until="networkidle")

            # Output filename like Bekasiak_fax.pdf
            pdf_name = f"{name.split()[0]}_fax.pdf"

            # Export to PDF (Letter size, margins same as your HTML)
            await page.pdf(
                path=pdf_name,
                format="Letter",
                margin={"top": "0.6in", "bottom": "0.6in", "left": "0.6in", "right": "0.6in"},
                print_background=True,
            )

            print(f"✅ Saved: {pdf_name}")

        await browser.close()

asyncio.run(main())
