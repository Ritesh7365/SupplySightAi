# Data Dictionary — `warehouse` schema

## Conventions

| Pattern | Meaning |
|---------|---------|
| `*_key` | Surrogate primary / foreign key (warehouse) |
| `*_id` / `*_bk` / `shipping_mode` / `calendar_date` | Natural business key |
| `source_system` | Always `'public'` for current ETL |
| `etl_loaded_at` | Warehouse load timestamp |
| `created_at` / `updated_at` | Warehouse row audit timestamps |

---

## Dimensions

### `dim_date`

| Column | Type | Description |
|--------|------|-------------|
| `date_key` | INTEGER PK | YYYYMMDD join key |
| `calendar_date` | DATE UK | Natural calendar date |
| `day_of_week` | SMALLINT | ISO day 1=Mon … 7=Sun |
| `day_name` | VARCHAR | Monday … Sunday |
| `day_of_month` | SMALLINT | 1–31 |
| `day_of_year` | SMALLINT | 1–366 |
| `week_of_year` | SMALLINT | ISO week |
| `month_number` | SMALLINT | 1–12 |
| `month_name` | VARCHAR | January … |
| `quarter_number` | SMALLINT | 1–4 |
| `quarter_name` | VARCHAR | Q1–Q4 |
| `year_number` | INTEGER | Calendar year |
| `is_weekend` | BOOLEAN | Sat/Sun |
| `is_month_end` | BOOLEAN | Last day of month |
| `year_month` | VARCHAR | `YYYY-MM` |

### `dim_department`

| Column | Type | Description |
|--------|------|-------------|
| `department_key` | BIGSERIAL PK | Surrogate |
| `department_id` | INTEGER UK | From `public.departments` |
| `department_name` | VARCHAR | Department label |

### `dim_category`

| Column | Type | Description |
|--------|------|-------------|
| `category_key` | BIGSERIAL PK | Surrogate |
| `category_id` | INTEGER UK | From `public.categories` |
| `category_name` | VARCHAR | Not unique in source |
| `department_id` | INTEGER | Lineage to source department |

### `dim_product`

| Column | Type | Description |
|--------|------|-------------|
| `product_key` | BIGSERIAL PK | Surrogate |
| `product_id` | INTEGER UK | Product Card Id |
| `product_name` | VARCHAR | Product name |
| `category_id` | INTEGER | Source category NK |
| `product_price` | NUMERIC | Catalog price |
| `product_status` | SMALLINT | 0 / 1 |
| `product_status_desc` | VARCHAR | Available / Not Available |
| `product_image_url` | TEXT | Optional image URL |

### `dim_customer`

| Column | Type | Description |
|--------|------|-------------|
| `customer_key` | BIGSERIAL PK | Surrogate |
| `customer_id` | INTEGER UK | Customer Id |
| `first_name` / `last_name` | VARCHAR | Name |
| `email` | VARCHAR | PII — protect in prod |
| `customer_segment` | VARCHAR | Consumer / Corporate / Home Office |
| `street` … `longitude` | mixed | Customer address / geo |

**Excluded from DW:** `password_mask`.

### `dim_location`

| Column | Type | Description |
|--------|------|-------------|
| `location_key` | BIGSERIAL PK | Surrogate |
| `location_bk` | CHAR(32) UK | MD5 of geo concatenation |
| `market` | VARCHAR | Order market |
| `order_region` | VARCHAR | Region |
| `order_country` | VARCHAR | Country |
| `order_state` | VARCHAR | State / province |
| `order_city` | VARCHAR | City |
| `order_zipcode` | VARCHAR | Often null |

### `dim_shipping`

| Column | Type | Description |
|--------|------|-------------|
| `shipping_key` | BIGSERIAL PK | Surrogate |
| `shipping_mode` | VARCHAR UK | e.g. Standard Class |
| `shipping_mode_group` | VARCHAR | Express / Standard / Other |

---

## Facts

### `fact_sales`

| Column | Type | Description |
|--------|------|-------------|
| `sales_key` | BIGSERIAL PK | Surrogate |
| `date_key` | INTEGER FK | → `dim_date` |
| `customer_key` | BIGINT FK | → `dim_customer` |
| `product_key` | BIGINT FK | → `dim_product` |
| `category_key` | BIGINT FK | → `dim_category` |
| `department_key` | BIGINT FK | → `dim_department` |
| `shipping_key` | BIGINT FK | → `dim_shipping` |
| `location_key` | BIGINT FK | → `dim_location` |
| `order_id` | INTEGER | Degenerate |
| `order_item_id` | INTEGER UK | Lineage / anti-dupe |
| `quantity` | INTEGER | Units |
| `sales` | NUMERIC | Line sales |
| `discount` | NUMERIC | Discount amount |
| `profit` | NUMERIC | Profit amount |
| `profit_ratio` | NUMERIC | Profit ratio |

### `fact_shipments`

| Column | Type | Description |
|--------|------|-------------|
| `shipment_key` | BIGSERIAL PK | Surrogate |
| `shipping_key` | BIGINT FK | → `dim_shipping` |
| `customer_key` | BIGINT FK | → `dim_customer` |
| `date_key` | INTEGER FK | → `dim_date` (order date) |
| `order_id` | INTEGER UK | Degenerate |
| `source_shipment_id` | BIGINT UK | From `shipments.shipment_id` |
| `actual_days` | INTEGER | Real shipping days |
| `scheduled_days` | INTEGER | Scheduled days |
| `late_delivery` | SMALLINT | 0/1 late risk |
| `delivery_status` | VARCHAR | Status label |
