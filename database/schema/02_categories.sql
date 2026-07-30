-- =============================================================================
-- SupplySight AI — categories
-- Purpose: Product category dimension, linked to departments.
-- Source: Category Id, Category Name; Department Id (1:1 category→department in DataCo).
-- =============================================================================

CREATE TABLE IF NOT EXISTS categories (
    category_id     INTEGER       PRIMARY KEY,
    category_name   VARCHAR(120)  NOT NULL,
    department_id   INTEGER       NOT NULL,
    created_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW(),

    -- Note: DataCo has duplicate category_name values across different category_id
    -- (e.g. Electronics → 13 and 37). Do not enforce UNIQUE(category_name).
    CONSTRAINT fk_categories_department
        FOREIGN KEY (department_id) REFERENCES departments (department_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

COMMENT ON TABLE categories IS
    'Product categories. Each category belongs to exactly one department in source data.';
COMMENT ON COLUMN categories.category_id IS
    'Natural key from DataCo Category Id / Product Category Id (equivalent in source).';
COMMENT ON COLUMN categories.department_id IS
    'FK to departments; derived from DataCo Department Id per category.';
