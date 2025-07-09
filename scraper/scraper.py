import asyncio
from sqlalchemy import select
from playwright.async_api import async_playwright
from db.models import Category,Product, PriceSnapshot, UnitType
from db.session import AsyncSessionLocal
from scraper.categories import CATEGORIES
import re
from datetime import datetime, timezone


def extract_glovo_id(name: str) -> str | None:
    match = re.search(r"\b(\d{5,})\b$", name.strip())
    return match.group(1) if match else None

async def parse_price(text: str):
    # Parse price like "7,49 лв." or "7.49 BGN" to float 7.49
    price_text = text.replace("лв.", "").replace("BGN", "").replace(",", ".").strip()
    try:
        return float(price_text)
    except Exception:
        return None

def convert_unit_type(raw_unit: str):
    unit = raw_unit.strip().lower()

    match unit:
        case "бр" | "бр.":
            return UnitType.PCS.value
        case "kg" | "кг":
            return UnitType.KG.value
        case "g" | "гр" | "г":
            return UnitType.G.value
        case "ml" | "мл":
            return UnitType.ML.value
        case "l" | "л":
            return UnitType.LITER.value
        case _:
            return unit

import re

def determine_category_from_name(product_name: str) -> str:
    keywords_to_subcategories = {
        "ориз": "Ориз",
        "боб": "Боб",
        "леща": "Леща",
    }
    product_name_lower = product_name.lower()
    for keyword, category in keywords_to_subcategories.items():
        if keyword in product_name_lower:
            return category

def parse_unit_price_from_name(name: str):
    """
    Attempts to extract quantity and unit from product name.
    Examples:
        "Яйца 10бр" → (10.0, "бр")
        "Вода 6x500ml" → (3000.0, "мл")
        "Сирене 250g" → (250.0, "г")
        "Мляко 4 x 1L" → (4000.0, "мл")
        "Кисело мляко 1,4 л" → (1400.0, "мл")
    Returns:
        total_quantity (float), unit (str)
    """
    patterns = [
        r"(\d+(?:[.,]\d+)?)\s*бр",  # 10бр or 10 бр
        r"(\d+(?:[.,]\d+)?)\s*[xхXХ]\s*(\d+(?:[.,]\d+)?)(ml|l|g|kg|мл|л|г|гр|кг)",  # 4x1L
        r"(\d+(?:[.,]\d+)?)\s*(ml|l|g|kg|мл|л|г|гр|кг)",  # 250g, 1,4 л
    ]

    name = name.lower().replace(",", ".").strip()
    for pattern in patterns:
        match = re.search(pattern, name)
        if match:
            groups = match.groups()
            if len(groups) == 1:
                qty = float(groups[0])
                return qty, convert_unit_type("бр")
            elif len(groups) == 2:
                qty = float(groups[0])
                unit = groups[1]
                return qty, convert_unit_type(unit)
            elif len(groups) == 3:
                count = float(groups[0])
                size = float(groups[1])
                unit = convert_unit_type(groups[2])
                return count * size, unit
    return None



async def scrape_category(page, url, category_name: str, limit: int = 10):
    print(f"Scraping category: {category_name} | {url}")
    await page.goto(url)
    await page.wait_for_selector("div[data-test-id='product-tile']")

    # Scroll to load more
    for _ in range(3):
        await page.mouse.wheel(0, 1000)
        await asyncio.sleep(1)

    product_cards = await page.query_selector_all("div[data-test-id='product-tile']")
    products = []

    for card in product_cards[:limit]:
        name_el = await card.query_selector("span.tile__description > span")
        name = await name_el.inner_text() if name_el else "Unknown"
        glovo_id = extract_glovo_id(name)

        # Get prices
        promo_el = await card.query_selector("span[data-test-id='product-price-effective']")
        promo_text = await promo_el.inner_text() if promo_el else None
        price_promo = await parse_price(promo_text) if promo_text else None

        regular_el = await card.query_selector("span[data-test-id='product-price-original']")
        regular_text = await regular_el.inner_text() if regular_el else None
        price_regular = await parse_price(regular_text) if regular_text else None

        if not price_regular and price_promo:
            price_regular = price_promo
            price_promo = None

        price_displayed = price_promo if price_promo else price_regular

        # Parse quantity/unit
        unit_price = None
        unit_type = None
        unit_quantity = None
        if name:
            parsed = parse_unit_price_from_name(name)
            if parsed:
                unit_quantity, unit_type = parsed
                if unit_quantity > 0 and price_displayed:
                    unit_price = round(price_displayed / unit_quantity, 2)

        # Get product image
        img_el = await card.query_selector("img[data-test-id='img-formats']")
        image_url = await img_el.get_attribute("src") if img_el else None

        products.append({
            "name": name,
            "glovo_id": glovo_id,
            "category": category_name,
            "image_url": image_url,
            "price_regular": price_regular,
            "price_promo": price_promo,
            "price_displayed": price_displayed,
            "unit_type": unit_type,
            "unit_quantity": unit_quantity,
            "unit_price": unit_price,
        })

    return products

async def save_products(products, grosery_store, category):
    async with AsyncSessionLocal() as session:
        for prod in products:
            if category == "Ориз и зърнено бобови":
                category = determine_category_from_name(prod["name"])
                if not category:
                    continue
            else:
                category = category.strip()

            result = await session.execute(
                select(Product).where(Product.name == prod["name"])
            )
            db_prod = result.scalars().first()

            result_cat = await session.execute(
                select(Category).where(Category.name == category)
            )
            
            db_category = result_cat.scalars().first()

            if not db_prod:
                db_prod = Product(
                    name=prod["name"],
                    glovo_id=prod["glovo_id"],
                    category_id=db_category.id,
                    image_url=prod["image_url"],
                    grosery_store=grosery_store,
                )
                session.add(db_prod)
                await session.commit()
                await session.flush()

            snapshot = PriceSnapshot(
                product_id=db_prod.id,
                timestamp=datetime.now(timezone.utc),
                price_regular=prod["price_regular"],
                price_promo=prod["price_promo"],
                price_displayed=prod["price_displayed"],
                unit_type=prod.get("unit_type"),
                unit_quantity=prod.get("unit_quantity"),
                unit_price_normalized=prod.get("unit_price"),
            )
            session.add(snapshot)

        await session.commit()


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        for grocery_store, categories in CATEGORIES.items():
            for cat in categories:
                category_name=cat["name"].strip()
                products = await scrape_category(
                    page, url=cat["url"], category_name=category_name, limit=cat["scrape_limit"]
                )
                print(f"Found {len(products)} products in category {cat['name']}")
                await save_products(products, grocery_store, category_name)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
