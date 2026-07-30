"""
Synthetic operations master data loader.

DataCo has no warehouse / inventory / vendor identifiers. This module generates
realistic masters into public.warehouses, public.inventory, public.vendors, and
public.vendor_products, preserving FKs to public.products.

Idempotent: truncates ops tables (not commerce tables) then reloads.
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from psycopg2.extensions import connection as PgConnection
from psycopg2.extras import execute_batch

logger = logging.getLogger("supplysight.postgres.seed_ops")

RNG_SEED = 20260730

WAREHOUSE_SITES: tuple[dict, ...] = (
    {"code": "WH-NYC-01", "name": "New York Metro DC", "city": "New York", "state": "NY", "country": "United States", "lat": 40.7128, "lon": -74.0060, "type": "Distribution Center", "capacity": 85000},
    {"code": "WH-LAX-01", "name": "Los Angeles West Hub", "city": "Los Angeles", "state": "CA", "country": "United States", "lat": 34.0522, "lon": -118.2437, "type": "Regional Hub", "capacity": 92000},
    {"code": "WH-CHI-01", "name": "Chicago Central DC", "city": "Chicago", "state": "IL", "country": "United States", "lat": 41.8781, "lon": -87.6298, "type": "Distribution Center", "capacity": 78000},
    {"code": "WH-DAL-01", "name": "Dallas South Hub", "city": "Dallas", "state": "TX", "country": "United States", "lat": 32.7767, "lon": -96.7970, "type": "Regional Hub", "capacity": 70000},
    {"code": "WH-ATL-01", "name": "Atlanta Southeast DC", "city": "Atlanta", "state": "GA", "country": "United States", "lat": 33.7490, "lon": -84.3880, "type": "Distribution Center", "capacity": 66000},
    {"code": "WH-SEA-01", "name": "Seattle Pacific Node", "city": "Seattle", "state": "WA", "country": "United States", "lat": 47.6062, "lon": -122.3321, "type": "Fulfillment Center", "capacity": 54000},
    {"code": "WH-MIA-01", "name": "Miami LatAm Gateway", "city": "Miami", "state": "FL", "country": "United States", "lat": 25.7617, "lon": -80.1918, "type": "Regional Hub", "capacity": 48000},
    {"code": "WH-DEN-01", "name": "Denver Mountain DC", "city": "Denver", "state": "CO", "country": "United States", "lat": 39.7392, "lon": -104.9903, "type": "Distribution Center", "capacity": 51000},
    {"code": "WH-BOS-01", "name": "Boston Northeast Node", "city": "Boston", "state": "MA", "country": "United States", "lat": 42.3601, "lon": -71.0589, "type": "Fulfillment Center", "capacity": 42000},
    {"code": "WH-PHX-01", "name": "Phoenix Southwest DC", "city": "Phoenix", "state": "AZ", "country": "United States", "lat": 33.4484, "lon": -112.0740, "type": "Distribution Center", "capacity": 58000},
    {"code": "WH-TOR-01", "name": "Toronto Canada Hub", "city": "Toronto", "state": "ON", "country": "Canada", "lat": 43.6532, "lon": -79.3832, "type": "Regional Hub", "capacity": 61000},
    {"code": "WH-MEX-01", "name": "Mexico City DC", "city": "Mexico City", "state": "CMX", "country": "Mexico", "lat": 19.4326, "lon": -99.1332, "type": "Distribution Center", "capacity": 55000},
    {"code": "WH-LON-01", "name": "London UK Hub", "city": "London", "state": "ENG", "country": "United Kingdom", "lat": 51.5074, "lon": -0.1278, "type": "Regional Hub", "capacity": 64000},
    {"code": "WH-FRA-01", "name": "Frankfurt EU DC", "city": "Frankfurt", "state": "HE", "country": "Germany", "lat": 50.1109, "lon": 8.6821, "type": "Distribution Center", "capacity": 72000},
    {"code": "WH-PAR-01", "name": "Paris West Fulfillment", "city": "Paris", "state": "IDF", "country": "France", "lat": 48.8566, "lon": 2.3522, "type": "Fulfillment Center", "capacity": 47000},
    {"code": "WH-MAD-01", "name": "Madrid Iberia DC", "city": "Madrid", "state": "MD", "country": "Spain", "lat": 40.4168, "lon": -3.7038, "type": "Distribution Center", "capacity": 43000},
    {"code": "WH-SIN-01", "name": "Singapore APAC Hub", "city": "Singapore", "state": "SG", "country": "Singapore", "lat": 1.3521, "lon": 103.8198, "type": "Regional Hub", "capacity": 68000},
    {"code": "WH-TYO-01", "name": "Tokyo East DC", "city": "Tokyo", "state": "13", "country": "Japan", "lat": 35.6762, "lon": 139.6503, "type": "Distribution Center", "capacity": 59000},
    {"code": "WH-SYD-01", "name": "Sydney Oceania Node", "city": "Sydney", "state": "NSW", "country": "Australia", "lat": -33.8688, "lon": 151.2093, "type": "Fulfillment Center", "capacity": 45000},
    {"code": "WH-BOM-01", "name": "Mumbai India Hub", "city": "Mumbai", "state": "MH", "country": "India", "lat": 19.0760, "lon": 72.8777, "type": "Regional Hub", "capacity": 62000},
)

VENDOR_TEMPLATES: tuple[dict, ...] = (
    {"prefix": "Northwind", "countries": [("United States", "Chicago"), ("United States", "Seattle"), ("Canada", "Toronto")]},
    {"prefix": "Pacific", "countries": [("Japan", "Tokyo"), ("Singapore", "Singapore"), ("Australia", "Sydney")]},
    {"prefix": "Atlantic", "countries": [("United Kingdom", "London"), ("Germany", "Frankfurt"), ("France", "Paris")]},
    {"prefix": "Andes", "countries": [("Mexico", "Mexico City"), ("Brazil", "Sao Paulo"), ("Chile", "Santiago")]},
    {"prefix": "Sahara", "countries": [("United Arab Emirates", "Dubai"), ("Egypt", "Cairo"), ("South Africa", "Johannesburg")]},
    {"prefix": "Silk", "countries": [("India", "Mumbai"), ("China", "Shanghai"), ("Vietnam", "Ho Chi Minh City")]},
    {"prefix": "Nordic", "countries": [("Sweden", "Stockholm"), ("Denmark", "Copenhagen"), ("Norway", "Oslo")]},
    {"prefix": "Iberia", "countries": [("Spain", "Madrid"), ("Portugal", "Lisbon"), ("Italy", "Milan")]},
)


@dataclass(frozen=True)
class SeedResult:
    warehouses: int
    inventory: int
    vendors: int
    vendor_products: int


def _fetch_products(conn: PgConnection) -> list[tuple[int, Decimal]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT product_id, product_price
            FROM public.products
            ORDER BY product_id
            """
        )
        rows = cur.fetchall()
    if not rows:
        raise RuntimeError(
            "public.products is empty. Load commerce CSVs before seeding operations masters."
        )
    return [(int(r[0]), Decimal(str(r[1]))) for r in rows]


def _truncate_ops(conn: PgConnection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            TRUNCATE TABLE
                public.inventory,
                public.vendor_products,
                public.warehouses,
                public.vendors
            RESTART IDENTITY CASCADE
            """
        )


def _insert_warehouses(conn: PgConnection, rng: random.Random) -> list[int]:
    rows = []
    for site in WAREHOUSE_SITES:
        # utilization seeded; refreshed after inventory load
        util = round(rng.uniform(48.0, 88.0), 2)
        rows.append(
            (
                site["code"],
                site["name"],
                site["city"],
                site["state"],
                site["country"],
                None,
                site["lat"],
                site["lon"],
                True,
                site["type"],
                site["capacity"],
                util,
            )
        )
    with conn.cursor() as cur:
        execute_batch(
            cur,
            """
            INSERT INTO public.warehouses (
                warehouse_code, warehouse_name, city, state_code, country,
                postal_code, latitude, longitude, is_active,
                warehouse_type, capacity, utilization_percent
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s
            )
            """,
            rows,
            page_size=100,
        )
        cur.execute("SELECT warehouse_id FROM public.warehouses ORDER BY warehouse_id")
        return [int(r[0]) for r in cur.fetchall()]


def _insert_vendors(conn: PgConnection, rng: random.Random, count: int = 50) -> list[int]:
    rows = []
    for i in range(1, count + 1):
        group = VENDOR_TEMPLATES[(i - 1) % len(VENDOR_TEMPLATES)]
        country, city = group["countries"][(i - 1) % len(group["countries"])]
        rating = round(rng.uniform(3.2, 4.9), 2)
        on_time = round(rng.uniform(78.0, 99.0), 2)
        lead = rng.randint(3, 28)
        risk = "LOW" if rating >= 4.4 and on_time >= 92 else (
            "MEDIUM" if rating >= 3.8 else ("HIGH" if rating >= 3.4 else "CRITICAL")
        )
        code = f"VN-{i:03d}"
        name = f"{group['prefix']} Supply {i:02d}"
        email = f"procurement@{code.lower().replace('-', '')}.example.com"
        phone = f"+1-555-{1000 + i:04d}"
        rows.append(
            (
                code,
                name,
                email,
                phone,
                country,
                city,
                risk,
                True,
                lead,
                rating,
                on_time,
            )
        )
    with conn.cursor() as cur:
        execute_batch(
            cur,
            """
            INSERT INTO public.vendors (
                vendor_code, vendor_name, contact_email, contact_phone,
                country, city, risk_tier, is_active,
                lead_time_days, rating, on_time_delivery_pct
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s
            )
            """,
            rows,
            page_size=100,
        )
        cur.execute("SELECT vendor_id FROM public.vendors ORDER BY vendor_id")
        return [int(r[0]) for r in cur.fetchall()]


def _insert_inventory(
    conn: PgConnection,
    rng: random.Random,
    warehouse_ids: Sequence[int],
    products: Sequence[tuple[int, Decimal]],
) -> int:
    """Every product in every warehouse with realistic stock profiles."""
    rows = []
    for warehouse_id in warehouse_ids:
        for product_id, _price in products:
            # ~6% intentionally out of stock / critically low for alerts
            roll = rng.random()
            if roll < 0.03:
                on_hand = 0
            elif roll < 0.08:
                on_hand = rng.randint(1, 8)
            else:
                on_hand = rng.randint(25, 420)

            reserved = 0 if on_hand == 0 else min(on_hand, rng.randint(0, max(1, on_hand // 8)))
            safety = rng.randint(10, 40)
            reorder_point = safety + rng.randint(5, 25)
            maximum = max(on_hand + rng.randint(40, 200), reorder_point * 3)
            reorder_qty = rng.randint(40, 160)
            rows.append(
                (
                    warehouse_id,
                    product_id,
                    on_hand,
                    reserved,
                    reorder_point,
                    reorder_qty,
                    safety,
                    maximum,
                )
            )

    with conn.cursor() as cur:
        execute_batch(
            cur,
            """
            INSERT INTO public.inventory (
                warehouse_id, product_id,
                quantity_on_hand, quantity_reserved,
                reorder_point, reorder_quantity,
                safety_stock, maximum_stock
            ) VALUES (
                %s, %s,
                %s, %s,
                %s, %s,
                %s, %s
            )
            """,
            rows,
            page_size=500,
        )
    return len(rows)


def _refresh_warehouse_utilization(conn: PgConnection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            """
            UPDATE public.warehouses w
            SET utilization_percent = sub.util,
                updated_at = NOW()
            FROM (
                SELECT
                    i.warehouse_id,
                    ROUND(
                        (SUM(i.quantity_on_hand) / NULLIF(w2.capacity, 0)) * 100,
                        2
                    ) AS util
                FROM public.inventory i
                INNER JOIN public.warehouses w2
                    ON w2.warehouse_id = i.warehouse_id
                GROUP BY i.warehouse_id, w2.capacity
            ) AS sub
            WHERE w.warehouse_id = sub.warehouse_id
            """
        )


def _insert_vendor_products(
    conn: PgConnection,
    rng: random.Random,
    vendor_ids: Sequence[int],
    products: Sequence[tuple[int, Decimal]],
) -> int:
    rows = []
    for product_id, price in products:
        n_vendors = rng.randint(2, 5)
        chosen = rng.sample(list(vendor_ids), k=min(n_vendors, len(vendor_ids)))
        preferred_idx = rng.randrange(len(chosen))
        for idx, vendor_id in enumerate(chosen):
            discount = Decimal(str(round(rng.uniform(0.55, 0.92), 4)))
            unit_cost = (price * discount).quantize(Decimal("0.0001"))
            lead = rng.randint(2, 35)
            moq = Decimal(rng.choice([10, 20, 25, 50, 100]))
            rows.append(
                (
                    vendor_id,
                    product_id,
                    f"SKU-{vendor_id:03d}-{product_id:04d}",
                    lead,
                    unit_cost,
                    idx == preferred_idx,
                    moq,
                )
            )

    with conn.cursor() as cur:
        execute_batch(
            cur,
            """
            INSERT INTO public.vendor_products (
                vendor_id, product_id, vendor_sku,
                lead_time_days, unit_cost, is_preferred,
                minimum_order_qty
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s,
                %s
            )
            """,
            rows,
            page_size=500,
        )
    return len(rows)


def seed_operations_masters(
    conn: PgConnection,
    *,
    vendor_count: int = 50,
    rng_seed: int = RNG_SEED,
) -> SeedResult:
    """
    Truncate and reload synthetic warehouses, inventory, vendors, vendor_products.
    Requires public.products to be populated.
    """
    rng = random.Random(rng_seed)
    products = _fetch_products(conn)
    logger.info("Seeding operations masters for %s products", len(products))

    _truncate_ops(conn)
    warehouse_ids = _insert_warehouses(conn, rng)
    vendor_ids = _insert_vendors(conn, rng, count=vendor_count)
    inv_count = _insert_inventory(conn, rng, warehouse_ids, products)
    _refresh_warehouse_utilization(conn)
    vp_count = _insert_vendor_products(conn, rng, vendor_ids, products)
    conn.commit()

    result = SeedResult(
        warehouses=len(warehouse_ids),
        inventory=inv_count,
        vendors=len(vendor_ids),
        vendor_products=vp_count,
    )
    logger.info(
        "Seeded warehouses=%s inventory=%s vendors=%s vendor_products=%s",
        result.warehouses,
        result.inventory,
        result.vendors,
        result.vendor_products,
    )
    return result


def counts(conn: PgConnection) -> dict[str, int]:
    out: dict[str, int] = {}
    with conn.cursor() as cur:
        for table in ("warehouses", "inventory", "vendors", "vendor_products"):
            cur.execute(f"SELECT COUNT(*) FROM public.{table}")
            out[table] = int(cur.fetchone()[0])
    return out
