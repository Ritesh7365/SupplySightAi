-- =============================================================================
-- SupplySight AI — warehouse.dim_date
-- Role: Shared calendar / time dimension for sales and shipment facts.
-- Grain: One row per calendar day.
-- Key design: date_key = YYYYMMDD integer (DW convention; natural & join key).
-- =============================================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_date (
    date_key            INTEGER         NOT NULL,
    calendar_date       DATE            NOT NULL,
    day_of_week         SMALLINT        NOT NULL,
    day_name            VARCHAR(10)     NOT NULL,
    day_of_month        SMALLINT        NOT NULL,
    day_of_year         SMALLINT        NOT NULL,
    week_of_year        SMALLINT        NOT NULL,
    month_number        SMALLINT        NOT NULL,
    month_name          VARCHAR(10)     NOT NULL,
    quarter_number      SMALLINT        NOT NULL,
    quarter_name        VARCHAR(2)      NOT NULL,
    year_number         INTEGER         NOT NULL,
    is_weekend          BOOLEAN         NOT NULL,
    is_month_end        BOOLEAN         NOT NULL,
    year_month          VARCHAR(7)      NOT NULL,
    -- Audit
    source_system       VARCHAR(50)     NOT NULL DEFAULT 'public',
    etl_loaded_at       TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT pk_dim_date PRIMARY KEY (date_key),
    CONSTRAINT uq_dim_date_calendar UNIQUE (calendar_date),
    CONSTRAINT ck_dim_date_key_format
        CHECK (date_key = TO_CHAR(calendar_date, 'YYYYMMDD')::INTEGER)
);

COMMENT ON TABLE warehouse.dim_date IS
    'Date dimension. Surrogate/join key date_key is YYYYMMDD; natural key is calendar_date.';
COMMENT ON COLUMN warehouse.dim_date.date_key IS
    'Integer surrogate key in YYYYMMDD form (e.g. 20180224).';
COMMENT ON COLUMN warehouse.dim_date.calendar_date IS
    'Natural business key — ISO calendar date.';
COMMENT ON COLUMN warehouse.dim_date.source_system IS
    'Origin of row generation (calendar built from public order/shipment dates).';
COMMENT ON COLUMN warehouse.dim_date.etl_loaded_at IS
    'Timestamp when the row was last loaded by warehouse ETL.';
