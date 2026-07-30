"""
SupplySight AI Copilot — Groq (LangChain) over analytics views.

Flow:
  1. Detect intent from the user question
  2. Pull relevant rows from analytics.* views
  3. Render readable context
  4. Call ChatGroq when GROQ_API_KEY is set
  5. Fall back to the rules engine on missing key / import / API failure
"""

from __future__ import annotations

import json
import time
from enum import Enum
from typing import Generator, List, Optional, Sequence

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.logging import get_logger
from app.schemas.ai import AiInsightResponse
from app.services.dashboard_service import DashboardService

logger = get_logger("services.ai")

SYSTEM_PROMPT = """You are SupplySight AI, an enterprise supply chain analytics assistant.

Never invent numbers.

Only answer using supplied analytics context.

If the requested information is unavailable, clearly state that.

Be concise.

Always explain business impact."""

SOURCE_EXECUTIVE = "analytics.vw_executive_dashboard"
SOURCE_SALES = "analytics.vw_sales_performance"
SOURCE_CUSTOMERS = "analytics.vw_customer_performance"
SOURCE_PRODUCTS = "analytics.vw_product_performance"
SOURCE_SHIPPING = "analytics.vw_shipping_performance"
SOURCE_GEOGRAPHY = "analytics.vw_geographic_performance"


class Intent(str, Enum):
    EXECUTIVE = "executive"
    SALES = "sales"
    CUSTOMERS = "customers"
    PRODUCTS = "products"
    SHIPPING = "shipping"
    GEOGRAPHY = "geography"
    FORECAST = "forecast"
    ANOMALY = "anomaly"
    INVENTORY = "inventory"
    GENERAL = "general"


def detect_intent(question: str) -> Intent:
    q = question.lower()
    if any(k in q for k in ("anomal", "outlier", "unusual", "spike")):
        return Intent.ANOMALY
    if any(k in q for k in ("forecast", "predict", "next month", "projection")):
        return Intent.FORECAST
    if any(k in q for k in ("ship", "late", "delay", "delivery", "carrier", "transit")):
        return Intent.SHIPPING
    if any(k in q for k in ("customer", "retention", "segment", "lifetime", "ltv")):
        return Intent.CUSTOMERS
    if any(k in q for k in ("product", "sku", "category", "department", "restock", "abc")):
        return Intent.PRODUCTS
    if any(k in q for k in ("region", "geo", "country", "market", "city", "state")):
        return Intent.GEOGRAPHY
    if any(k in q for k in ("inventory", "stock", "warehouse", "vendor", "supplier")):
        return Intent.INVENTORY
    if any(k in q for k in ("sales", "revenue", "monthly", "order volume", "aov")):
        return Intent.SALES
    if any(k in q for k in ("profit", "margin", "kpi", "executive", "overview", "snapshot")):
        return Intent.EXECUTIVE
    return Intent.GENERAL


def _row_to_line(row: dict) -> str:
    parts = [f"{k}={v}" for k, v in row.items() if v is not None]
    return "- " + ", ".join(parts)


def _format_section(title: str, rows: Sequence[dict]) -> str:
    if not rows:
        return f"### {title}\n(no rows available)\n"
    body = "\n".join(_row_to_line(dict(r)) for r in rows)
    return f"### {title}\n{body}\n"


class AiInsightService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    # ------------------------------------------------------------------ context
    def _fetch_dicts(self, sql: str, params: Optional[dict] = None) -> List[dict]:
        try:
            rows = self.db.execute(text(sql), params or {}).mappings().all()
            return [dict(r) for r in rows]
        except Exception:  # noqa: BLE001
            logger.warning("Analytics context query failed", exc_info=True)
            return []

    def _collect_context(self, intent: Intent) -> tuple[str, List[str]]:
        sources: List[str] = []
        sections: List[str] = []

        def add(source: str, title: str, sql: str, params: Optional[dict] = None) -> None:
            rows = self._fetch_dicts(sql, params)
            sections.append(_format_section(title, rows))
            if source not in sources:
                sources.append(source)

        # Always include executive KPIs as grounding
        add(
            SOURCE_EXECUTIVE,
            "Executive dashboard (vw_executive_dashboard)",
            """
            SELECT total_sales, total_profit, total_orders, total_customers,
                   average_order_value, late_delivery_pct, total_shipments,
                   late_shipments, overall_profit_margin_pct, refreshed_at
            FROM analytics.vw_executive_dashboard
            LIMIT 1
            """,
        )

        need_sales = intent in {
            Intent.SALES,
            Intent.EXECUTIVE,
            Intent.FORECAST,
            Intent.ANOMALY,
            Intent.GENERAL,
            Intent.INVENTORY,
        }
        need_customers = intent in {Intent.CUSTOMERS, Intent.ANOMALY, Intent.GENERAL}
        need_products = intent in {
            Intent.PRODUCTS,
            Intent.INVENTORY,
            Intent.ANOMALY,
            Intent.GENERAL,
            Intent.EXECUTIVE,
        }
        need_shipping = intent in {
            Intent.SHIPPING,
            Intent.ANOMALY,
            Intent.GENERAL,
            Intent.EXECUTIVE,
            Intent.FORECAST,
        }
        need_geo = intent in {Intent.GEOGRAPHY, Intent.ANOMALY, Intent.SALES, Intent.GENERAL}

        if need_sales:
            add(
                SOURCE_SALES,
                "Sales performance — recent months (vw_sales_performance)",
                """
                SELECT year_month, month_name, market, region, sales, profit,
                       order_count, customer_count, average_order_value, profit_margin_pct
                FROM analytics.vw_sales_performance
                ORDER BY year_number DESC, month_number DESC, sales DESC
                LIMIT 24
                """,
            )

        if need_customers:
            add(
                SOURCE_CUSTOMERS,
                "Top customers (vw_customer_performance)",
                """
                SELECT customer_name, customer_segment, revenue, profit,
                       order_count, average_order_value, revenue_rank
                FROM analytics.vw_customer_performance
                ORDER BY revenue_rank
                LIMIT 15
                """,
            )

        if need_products:
            add(
                SOURCE_PRODUCTS,
                "Top products (vw_product_performance)",
                """
                SELECT product_name, category_name, department_name, sales, profit,
                       units_sold, best_selling_rank, profit_margin_pct
                FROM analytics.vw_product_performance
                ORDER BY best_selling_rank
                LIMIT 15
                """,
            )

        if need_shipping:
            add(
                SOURCE_SHIPPING,
                "Shipping performance by mode (vw_shipping_performance)",
                """
                SELECT shipping_mode, shipping_mode_group, shipment_count,
                       avg_shipping_time_days, late_delivery_count,
                       late_delivery_risk_pct, delay_rate_pct,
                       on_time_status_count, delayed_shipment_count
                FROM analytics.vw_shipping_performance
                ORDER BY late_delivery_risk_pct DESC NULLS LAST
                LIMIT 20
                """,
            )

        if need_geo:
            add(
                SOURCE_GEOGRAPHY,
                "Geographic performance (vw_geographic_performance)",
                """
                SELECT market, region, country, sales, profit, order_count,
                       customer_count, profit_margin_pct, geo_sales_rank
                FROM analytics.vw_geographic_performance
                ORDER BY geo_sales_rank
                LIMIT 20
                """,
            )

        context = (
            f"Intent detected: {intent.value}\n\n"
            + "\n".join(sections)
            + "\nUse only the figures above. Do not invent metrics."
        )
        return context, sources

    # ------------------------------------------------------------------ rules
    def _rule_based(self, question: str) -> str:
        q = question.lower()
        svc = DashboardService(self.db)
        exec_kpi = svc.get_executive()
        shipping = svc.get_shipping().data
        categories = svc.get_revenue_by_category(limit=5).data

        if "profit" in q and ("drop" in q or "down" in q or "decline" in q):
            margin = exec_kpi.overall_profit_margin_pct
            return (
                f"Current gross profit is {exec_kpi.total_profit} with overall margin "
                f"{margin}%. Late delivery sits at {exec_kpi.late_delivery_pct}%, which "
                "raises expedite and discount pressure. Review top categories "
                f"({', '.join(c.name for c in categories[:3])}) for margin erosion and "
                "compare profit trend on the Forecasting page."
            )

        if "ship" in q or "delay" in q or "late" in q:
            if not shipping:
                return "Shipping analytics are empty. Refresh analytics.vw_shipping_performance."
            worst = max(shipping, key=lambda s: float(s.late_delivery_risk_pct or 0))
            return (
                f"Late delivery is {exec_kpi.late_delivery_pct}% overall "
                f"({exec_kpi.late_shipments} of {exec_kpi.total_shipments} shipments). "
                f"Highest risk mode is {worst.shipping_mode} at "
                f"{worst.late_delivery_risk_pct}% late with avg transit "
                f"{worst.avg_shipping_time_days} days. Prioritize carrier SLAs and "
                "capacity on that mode."
            )

        if "predict" in q or "forecast" in q or "next month" in q:
            return (
                "Open Forecasting for the revenue projection (Prophet when installed, "
                "otherwise linear trend with confidence intervals). Use the latest "
                f"monthly sales history; current revenue baseline is {exec_kpi.total_sales}."
            )

        if "restock" in q or "inventory" in q:
            alerts = svc.get_inventory_alerts(limit=10)
            if alerts.count == 0:
                return (
                    "Inventory balances are not populated in analytics context for this "
                    "rules path. Seed public.inventory or ask about product sales ranks."
                )
            names = ", ".join(a.product_name for a in alerts.data[:5])
            return (
                f"There are {alerts.out_of_stock_count} out-of-stock and "
                f"{alerts.low_stock_count} low-stock SKUs. Restock candidates: {names}."
            )

        if "warehouse" in q or "inefficient" in q:
            return (
                f"Network snapshot from executive KPIs: revenue {exec_kpi.total_sales}, "
                f"late delivery {exec_kpi.late_delivery_pct}%. Use the Warehouses page for "
                "capacity and utilization once operations masters are seeded."
            )

        if "anomal" in q:
            return (
                f"Watch late delivery at {exec_kpi.late_delivery_pct}% and margin at "
                f"{exec_kpi.overall_profit_margin_pct}%. Modes with elevated late risk "
                "and categories with falling profit are the primary anomaly signals."
            )

        top_cat = categories[0].name if categories else "n/a"
        return (
            f"SupplySight snapshot — revenue {exec_kpi.total_sales}, profit "
            f"{exec_kpi.total_profit}, orders {exec_kpi.total_orders}, customers "
            f"{exec_kpi.total_customers}, late delivery {exec_kpi.late_delivery_pct}%. "
            f"Leading category: {top_cat}. Ask about profit, shipping, forecasts, "
            "restocking, or anomalies for a deeper brief."
        )

    # -------------------------------------------------------------------- Groq
    def _groq_enabled(self) -> bool:
        key = (self.settings.groq_api_key or "").strip()
        provider = (self.settings.ai_provider or "groq").strip().lower()
        return bool(key) and provider in {"groq", "langchain-groq", "langchain_groq"}

    def _build_chat_groq(self):
        from langchain_groq import ChatGroq

        return ChatGroq(
            api_key=self.settings.groq_api_key,
            model=self.settings.ai_model,
            temperature=0.2,
        )

    def _extract_usage(self, result: object) -> tuple[Optional[int], Optional[int]]:
        prompt_tokens = completion_tokens = None
        meta = getattr(result, "response_metadata", None) or {}
        usage = meta.get("token_usage") or meta.get("usage") or {}
        if isinstance(usage, dict):
            prompt_tokens = usage.get("prompt_tokens") or usage.get("input_tokens")
            completion_tokens = usage.get("completion_tokens") or usage.get("output_tokens")
        usage_meta = getattr(result, "usage_metadata", None) or {}
        if isinstance(usage_meta, dict):
            prompt_tokens = prompt_tokens or usage_meta.get("input_tokens")
            completion_tokens = completion_tokens or usage_meta.get("output_tokens")
        return (
            int(prompt_tokens) if prompt_tokens is not None else None,
            int(completion_tokens) if completion_tokens is not None else None,
        )

    def _groq_answer(
        self,
        question: str,
        context: str,
    ) -> tuple[Optional[str], Optional[int], Optional[int], float]:
        """Returns (answer, prompt_tokens, completion_tokens, elapsed_ms)."""
        started = time.perf_counter()
        if not self._groq_enabled():
            return None, None, None, 0.0

        try:
            from langchain_core.prompts import ChatPromptTemplate
        except Exception:  # noqa: BLE001
            logger.info("langchain_core unavailable; using rules engine")
            return None, None, None, (time.perf_counter() - started) * 1000

        try:
            llm = self._build_chat_groq()
        except Exception:  # noqa: BLE001
            logger.warning("ChatGroq init failed; falling back to rules", exc_info=True)
            return None, None, None, (time.perf_counter() - started) * 1000

        try:
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", SYSTEM_PROMPT),
                    (
                        "human",
                        "Analytics context:\n{context}\n\nUser question:\n{question}",
                    ),
                ]
            )
            chain = prompt | llm
            result = chain.invoke({"context": context, "question": question})
            elapsed_ms = (time.perf_counter() - started) * 1000
            prompt_tokens, completion_tokens = self._extract_usage(result)
            content = getattr(result, "content", None)
            answer = content if isinstance(content, str) else str(content)
            logger.info(
                "Groq response model=%s elapsed_ms=%.1f prompt_tokens=%s completion_tokens=%s",
                self.settings.ai_model,
                elapsed_ms,
                prompt_tokens,
                completion_tokens,
            )
            return answer, prompt_tokens, completion_tokens, elapsed_ms
        except Exception:  # noqa: BLE001
            elapsed_ms = (time.perf_counter() - started) * 1000
            logger.warning(
                "Groq invoke failed after %.1fms; falling back to rules",
                elapsed_ms,
                exc_info=True,
            )
            return None, None, None, elapsed_ms

    def stream_groq(
        self,
        question: str,
        context: str,
    ) -> Generator[str, None, None]:
        """Yield answer chunks from Groq; yields nothing if unavailable."""
        if not self._groq_enabled():
            return

        try:
            from langchain_core.prompts import ChatPromptTemplate

            llm = self._build_chat_groq()
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", SYSTEM_PROMPT),
                    (
                        "human",
                        "Analytics context:\n{context}\n\nUser question:\n{question}",
                    ),
                ]
            )
            chain = prompt | llm
            started = time.perf_counter()
            for chunk in chain.stream({"context": context, "question": question}):
                text_part = getattr(chunk, "content", None)
                if text_part:
                    yield str(text_part)
            logger.info(
                "Groq stream completed model=%s elapsed_ms=%.1f",
                self.settings.ai_model,
                (time.perf_counter() - started) * 1000,
            )
        except Exception:  # noqa: BLE001
            logger.warning("Groq stream failed", exc_info=True)
            return

    # ------------------------------------------------------------------- public
    def ask(self, question: str) -> AiInsightResponse:
        started = time.perf_counter()
        intent = detect_intent(question)
        context, sources = self._collect_context(intent)

        answer, prompt_tokens, completion_tokens, groq_ms = self._groq_answer(
            question, context
        )
        if answer:
            return AiInsightResponse(
                question=question,
                answer=answer,
                sources=sources,
                model=self.settings.ai_model,
                intent=intent.value,
                response_time_ms=round(groq_ms or (time.perf_counter() - started) * 1000, 2),
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )

        rules_answer = self._rule_based(question)
        elapsed_ms = (time.perf_counter() - started) * 1000
        logger.info(
            "Rules-engine response intent=%s elapsed_ms=%.1f",
            intent.value,
            elapsed_ms,
        )
        return AiInsightResponse(
            question=question,
            answer=rules_answer,
            sources=sources
            or [
                SOURCE_EXECUTIVE,
                SOURCE_SHIPPING,
                SOURCE_PRODUCTS,
            ],
            model="rules+analytics",
            intent=intent.value,
            response_time_ms=round(elapsed_ms, 2),
            prompt_tokens=None,
            completion_tokens=None,
        )

    def ask_stream_events(self, question: str) -> Generator[str, None, None]:
        """
        SSE event generator for streaming answers.

        Falls back to a single rules-engine payload if Groq is unavailable.
        """
        intent = detect_intent(question)
        context, sources = self._collect_context(intent)
        yielded = False

        if self._groq_enabled():
            try:
                meta = json.dumps({"model": self.settings.ai_model, "intent": intent.value})
                yield f"event: meta\ndata: {meta}\n\n"
                for chunk in self.stream_groq(question, context):
                    yielded = True
                    payload = json.dumps({"token": chunk})
                    yield f"data: {payload}\n\n"
                if yielded:
                    done = json.dumps({"sources": sources})
                    yield f"event: done\ndata: {done}\n\n"
                    return
            except Exception:  # noqa: BLE001
                logger.warning("Streaming path failed; using rules fallback", exc_info=True)

        rules = self._rule_based(question)
        meta = json.dumps({"model": "rules+analytics", "intent": intent.value})
        yield f"event: meta\ndata: {meta}\n\n"
        yield f"data: {json.dumps({'token': rules})}\n\n"
        yield f"event: done\ndata: {json.dumps({'fallback': True, 'sources': sources})}\n\n"