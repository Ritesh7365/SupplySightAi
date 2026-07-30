# SupplySight AI — DataCo → PostgreSQL Column Mapping

Maps every column in `DataCoSupplyChainDataset.csv` to its destination table and column.  
Placeholder tables (`warehouses`, `inventory`, `vendors`) have **no** DataCo source columns.

| # | DataCo Column | Destination Table | Destination Column | Notes |
|---|---------------|-------------------|--------------------|-------|
| 1 | Type | `orders` | `transaction_type` | Payment/transaction type |
| 2 | Days for shipping (real) | `shipments` | `days_for_shipping_real` | Actual ship days |
| 3 | Days for shipment (scheduled) | `shipments` | `days_for_shipment_scheduled` | Scheduled ship days |
| 4 | Benefit per order | `order_items` | `benefit_amount` | Varies within some orders in source → line grain |
| 5 | Sales per customer | `order_items` | `sales_per_customer` | Denormalized source metric; retained for lineage |
| 6 | Delivery Status | `shipments` | `delivery_status` | Advance / Late / Canceled / On time |
| 7 | Late_delivery_risk | `shipments` | `late_delivery_risk` | 0/1 flag |
| 8 | Category Id | `categories` | `category_id` | Also equals Product Category Id |
| 9 | Category Name | `categories` | `category_name` | |
| 10 | Customer City | `customers` | `city` | |
| 11 | Customer Country | `customers` | `country` | |
| 12 | Customer Email | `customers` | `email` | **PII** |
| 13 | Customer Fname | `customers` | `first_name` | |
| 14 | Customer Id | `customers` | `customer_id` | PK |
| 15 | Customer Lname | `customers` | `last_name` | Rare nulls in source |
| 16 | Customer Password | `customers` | `password_mask` | **Sensitive** |
| 17 | Customer Segment | `customers` | `customer_segment` | Consumer / Corporate / Home Office |
| 18 | Customer State | `customers` | `state_code` | |
| 19 | Customer Street | `customers` | `street` | |
| 20 | Customer Zipcode | `customers` | `zipcode` | Stored as varchar |
| 21 | Department Id | `departments` | `department_id` | Also FK path via categories |
| 22 | Department Name | `departments` | `department_name` | |
| 23 | Latitude | `customers` | `latitude` | Per-customer unique in source |
| 24 | Longitude | `customers` | `longitude` | Per-customer unique in source |
| 25 | Market | `orders` | `market` | |
| 26 | Order City | `orders` | `order_city` | Delivery city |
| 27 | Order Country | `orders` | `order_country` | |
| 28 | Order Customer Id | `orders` | `customer_id` | Equals Customer Id (validated) |
| 29 | order date (DateOrders) | `orders` | `order_date` | Parsed timestamp |
| 30 | Order Id | `orders` | `order_id` | PK; FK from items/shipments |
| 31 | Order Item Cardprod Id | `order_items` | `product_id` | Equals Product Card Id |
| 32 | Order Item Discount | `order_items` | `discount_amount` | |
| 33 | Order Item Discount Rate | `order_items` | `discount_rate` | |
| 34 | Order Item Id | `order_items` | `order_item_id` | PK; source row grain |
| 35 | Order Item Product Price | `order_items` | `unit_price` | Price without discount |
| 36 | Order Item Profit Ratio | `order_items` | `profit_ratio` | |
| 37 | Order Item Quantity | `order_items` | `quantity` | |
| 38 | Sales | `order_items` | `sales` | |
| 39 | Order Item Total | `order_items` | `order_item_total` | |
| 40 | Order Profit Per Order | `order_items` | `profit_amount` | Varies within some orders → line grain |
| 41 | Order Region | `orders` | `order_region` | |
| 42 | Order State | `orders` | `order_state` | |
| 43 | Order Status | `orders` | `order_status` | |
| 44 | Order Zipcode | `orders` | `order_zipcode` | High missingness |
| 45 | Product Card Id | `products` | `product_id` | PK |
| 46 | Product Category Id | `products` | `category_id` | Equals Category Id |
| 47 | Product Description | `products` | `product_description` | 100% null in extract |
| 48 | Product Image | `products` | `product_image_url` | |
| 49 | Product Name | `products` | `product_name` | |
| 50 | Product Price | `products` | `product_price` | Catalog price |
| 51 | Product Status | `products` | `product_status` | 0 available / 1 unavailable |
| 52 | shipping date (DateOrders) | `shipments` | `shipping_date` | Parsed timestamp |
| 53 | Shipping Mode | `shipments` | `shipping_mode` | Standard / First / Second / Same Day |

## Unmapped destination entities (by design)

| Table | Reason |
|-------|--------|
| `warehouses` | No warehouse identifiers in DataCo |
| `inventory` | No on-hand quantities by location (only product_status flag) |
| `vendors` / `vendor_products` | No supplier identifiers in DataCo |

## Surrogate / system columns (not from DataCo)

All tables include `created_at` / `updated_at`.  
`shipments.shipment_id`, `warehouses.warehouse_id`, `inventory.inventory_id`, `vendors.vendor_id`, `vendor_products.vendor_product_id` are surrogates.
