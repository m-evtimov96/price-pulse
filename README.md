# Price Pulse

## 1. Overview

This project is built to **periodically scrape product prices** from several stores in Bulgaria using the Glovo platform. On a weekly or configurable schedule, it collects data for a predefined set of categories (e.g. eggs, milk, etc.), scraping the **top N products** per category.

Each snapshot includes:
- Product information (name, image_url, etc)
- Regular price
- Promotional price (if available)
- Price per unit (1 pice, 1 kg, 1 l, etc)

Over time, these snapshots can be compared to analyze **price trends**, track promotions, and observe how the prices of certain products evolve.

The goal is to provide a lightweight, structured foundation for building dashboards, alerts, or reports about local grocery pricing.


## 2. Models

This project uses two main models: `Product` and `PriceSnapshot`. These are designed to track product pricing over time for analysis and historical comparison.

---

### `Product`

Represents a unique product.

- `id`: UUID, primary key
- `glovo_id`: Optional string identifier from Glovo (if available)
- `name`: Product name (e.g. "Хоризонт Кокоши яйца М 10бр")
- `category`: The product’s category (e.g. "Eggs", "Milk")
- `image_url`: URL of the product image

Each `Product` is linked to many `PriceSnapshot`s, forming a history of price changes.

---

### `PriceSnapshot`

Represents a snapshot of product prices at a specific point in time.

- `id`: UUID, primary key
- `product_id`: Foreign key to the `Product`
- `timestamp`: When the snapshot was taken (auto-generated on scrape)

#### Price Fields:
- `price_regular`: The standard (non-discounted) price
- `price_promo`: Promotional price, if available
- `price_displayed`: The price currently shown (usually promo if available)

#### Unit Fields:
- `unit_type`: Type of unit (e.g. "бр", "кг", "л")
- `unit_quantity`: Quantity per unit (e.g. 10 for a 10-pack of eggs)
- `unit_price_normalized`: Price per base unit, normalized for comparison

These models allow the system to store detailed pricing and unit data for tracking price movements over time.


## 3. Scrapers

Currently, the project includes a scraper specifically for Glovo’s **Kaufland** store in Sofia. More scrapers for other stores will be implemented in the future.

### How It Works

- The scraper loads category definitions from `categories.py` (temporary format, to be revamped).
- For each configured category, it navigates to the corresponding Glovo URL and extracts product tiles.
- From each product tile, it collects:
  - Product name
  - Glovo product ID
  - Image URL
  - Regular price
  - Promo price (if available)
  - Displayed price
  - Unit type and quantity (e.g. “10 бр”, “1 л”)
- The product is either:
  - Inserted into the database if it’s new, or
  - Matched by its `name` if it already exists
- A new `PriceSnapshot` is created and stored for every product with the current timestamp.

### Scheduling

The scraper is currently run **manually** (e.g. via CLI or script). In the future, automated scheduling (e.g. using Prefect or cron) will be introduced to run it periodically (e.g. weekly).

### Categories

Categories are currently defined statically in the `categories.py` file. This setup is temporary and will be replaced with a more flexible system, possibly stored in the database or a dynamic config format.


## 4. Installation

Follow these steps to set up and run the project locally:

### 1. Prerequisites

- Python 3.13
- `uv` (for environment and package management)
- SQLite (used for local development; PostgreSQL will be used in production)

### 2. Clone the repository

```bash
git clone <your-repo-url>
cd <your-repo-directory>
```

### 3. Install Dependencies

Install [UV](https://docs.astral.sh/uv/)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Setup environment and install packages
```bash
uv sync --locked
```

### 4. Create initial database tables

Start the FastAPI app which will create the tables on startup:
```bash
uv run uvicorn main:app --reload
```
You can stop the server after the tables are created.

### 5. Run the Scraper manually

```bash
uv run python scraper/kaufland_glovo_scraper.py
```

