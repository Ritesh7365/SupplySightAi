# SupplySight AI — Entity Relationship Diagram

**Database:** PostgreSQL  
**Model style:** Normalized 3NF-oriented OLTP/analytics hybrid (star-friendly facts + dimensions)  
**Source extract:** DataCo Supply Chain Dataset

---

## 1. Tables Overview

| Table | Role | Populated from DataCo? |
|-------|------|------------------------|
| `departments` | Merchandising department dimension | Yes |
| `categories` | Product category dimension | Yes |
| `products` | Product catalog | Yes |
| `customers` | Customer master | Yes |
| `orders` | Order header | Yes |
| `order_items` | Order line facts (primary grain) | Yes |
| `shipments` | Delivery / shipping profile | Yes |
| `warehouses` | Warehouse master | **No — placeholder** |
| `inventory` | Stock balances | **No — placeholder** |
| `vendors` | Supplier master | **No — placeholder** |
| `vendor_products` | Vendor–SKU bridge | **No — placeholder** |

---

## 2. Primary Keys

| Table | PK |
|-------|----|
| departments | `department_id` |
| categories | `category_id` |
| products | `product_id` (= Product Card Id) |
| customers | `customer_id` |
| orders | `order_id` |
| order_items | `order_item_id` |
| shipments | `shipment_id` (surrogate) + UNIQUE(`order_id`) |
| warehouses | `warehouse_id` |
| inventory | `inventory_id` |
| vendors | `vendor_id` |
| vendor_products | `vendor_product_id` |

---

## 3. Foreign Keys & Cardinality

| Relationship | Cardinality | FK |
|--------------|-------------|-----|
| departments → categories | 1 : N | `categories.department_id` |
| categories → products | 1 : N | `products.category_id` |
| customers → orders | 1 : N | `orders.customer_id` |
| orders → order_items | 1 : N | `order_items.order_id` |
| products → order_items | 1 : N | `order_items.product_id` |
| orders → shipments | 1 : 1 (current extract) | `shipments.order_id` UNIQUE |
| warehouses → inventory | 1 : N | `inventory.warehouse_id` |
| products → inventory | 1 : N | `inventory.product_id` |
| vendors → vendor_products | 1 : N | `vendor_products.vendor_id` |
| products → vendor_products | 1 : N | `vendor_products.product_id` |

---

## 4. Mermaid ER Diagram

```mermaid
erDiagram
    DEPARTMENTS ||--o{ CATEGORIES : contains
    CATEGORIES ||--o{ PRODUCTS : classifies
    CUSTOMERS ||--o{ ORDERS : places
    ORDERS ||--o{ ORDER_ITEMS : includes
    PRODUCTS ||--o{ ORDER_ITEMS : sold_as
    ORDERS ||--|| SHIPMENTS : fulfilled_by
    WAREHOUSES ||--o{ INVENTORY : stocks
    PRODUCTS ||--o{ INVENTORY : stocked_in
    VENDORS ||--o{ VENDOR_PRODUCTS : supplies
    PRODUCTS ||--o{ VENDOR_PRODUCTS : sourced_from

    DEPARTMENTS {
        int department_id PK
        varchar department_name
    }
    CATEGORIES {
        int category_id PK
        varchar category_name
        int department_id FK
    }
    PRODUCTS {
        int product_id PK
        varchar product_name
        int category_id FK
        numeric product_price
        smallint product_status
    }
    CUSTOMERS {
        int customer_id PK
        varchar first_name
        varchar last_name
        varchar customer_segment
        varchar country
    }
    ORDERS {
        int order_id PK
        int customer_id FK
        timestamp order_date
        varchar order_status
        varchar market
    }
    ORDER_ITEMS {
        int order_item_id PK
        int order_id FK
        int product_id FK
        int quantity
        numeric sales
        numeric order_item_total
    }
    SHIPMENTS {
        bigint shipment_id PK
        int order_id FK
        varchar shipping_mode
        varchar delivery_status
        smallint late_delivery_risk
    }
    WAREHOUSES {
        int warehouse_id PK
        varchar warehouse_code
        varchar warehouse_name
    }
    INVENTORY {
        bigint inventory_id PK
        int warehouse_id FK
        int product_id FK
        numeric quantity_on_hand
    }
    VENDORS {
        int vendor_id PK
        varchar vendor_code
        varchar vendor_name
    }
    VENDOR_PRODUCTS {
        bigint vendor_product_id PK
        int vendor_id FK
        int product_id FK
    }
```

---

## 5. Design Notes

- **Analytic grain:** `order_items` (180,519 unique `Order Item Id` values in source).
- **Shipment 1:1:** Current extract has one shipping profile per `Order Id`; schema allows future multi-parcel by dropping/relaxing uniqueness if needed.
- **Placeholders:** `warehouses`, `inventory`, `vendors` are production-shaped but intentionally empty until external feeds arrive.
- **No fabricated business rows** for placeholder tables.
