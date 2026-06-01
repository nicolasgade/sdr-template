#!/usr/bin/env python3
"""Analyze profitability for marketing campaigns.

Usage:
    python3 execution/analyze_campaign_profitability.py \
        --campaign "Campaign Name" \
        --client "Client Name" \
        --sku "sku_key" \
        --baseline-units 100 \
        --target-units 200 \
        --campaign-cost 5000 \
        [--unit-price 100] \
        [--unit-cost 70]

Setup:
    1. Edit SKU_DEFAULTS with your actual unit costs
    2. Edit CLIENT_PRICES with your client-specific pricing
    3. Run with the appropriate flags
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


# TODO: Replace with your actual SKU costs
SKU_DEFAULTS = {
    "sku_1": {"unit_cost": 0.00},  # e.g., cost per unit for SKU 1
    "sku_2": {"unit_cost": 0.00},  # e.g., cost per unit for SKU 2
    "sku_3": {"unit_cost": 0.00},  # e.g., cost per unit for SKU 3
}

# TODO: Replace with your actual client pricing
# Key: (client_name_lowercase, sku_key) → wholesale price per unit
CLIENT_PRICES = {
    # ("client_1", "sku_1"): 100.0,
    # ("client_1", "sku_2"): 75.0,
    # ("client_2", "sku_1"): 98.0,
}


def normalize(value: str) -> str:
    return " ".join(value.lower().strip().split())


def default_price(client: str, sku: str) -> float | None:
    return CLIENT_PRICES.get((normalize(client), normalize(sku)))


def default_cost(sku: str) -> float | None:
    config = SKU_DEFAULTS.get(normalize(sku))
    return config["unit_cost"] if config else None


def money(value: float) -> str:
    return f"${value:,.2f}"


def percent(value: float) -> str:
    return f"{value:.1%}"


def recommendation(
    roi: float,
    margin_pct: float,
    net_contribution: float,
    break_even_total_units: int,
    target_units: int,
) -> tuple[str, str]:
    if margin_pct < 0.35:
        return "No go", "Margen unitario menor a 35%."
    if net_contribution < 0:
        return "No go", "La campaña no cubre su costo con el margen incremental esperado."
    if break_even_total_units > target_units:
        return "No go", "El punto de equilibrio supera la meta propuesta."
    if roi < 0.25:
        return "Go with constraints", "ROI positivo pero ajustado; cuidar ejecución, inventario y cobranza."
    return "Go", "Rentabilidad positiva con margen de seguridad razonable."


def analyze(args: argparse.Namespace) -> dict[str, object]:
    unit_price = args.unit_price if args.unit_price is not None else default_price(args.client, args.sku)
    unit_cost = args.unit_cost if args.unit_cost is not None else default_cost(args.sku)

    if unit_price is None:
        raise ValueError("Falta precio unitario. Pásalo con --unit-price.")
    if unit_cost is None:
        raise ValueError("Falta costo unitario. Pásalo con --unit-cost.")

    incremental_units = args.target_units - args.baseline_units
    margin_per_unit = unit_price - unit_cost
    if margin_per_unit <= 0:
        raise ValueError("El margen por unidad es cero o negativo. Revisar precio/costo.")

    margin_pct = margin_per_unit / unit_cost
    incremental_margin = incremental_units * margin_per_unit
    break_even_incremental_units = math.ceil(args.campaign_cost / margin_per_unit)
    break_even_total_units = args.baseline_units + break_even_incremental_units
    net_contribution = incremental_margin - args.campaign_cost
    roi = net_contribution / args.campaign_cost if args.campaign_cost else float("inf")
    total_campaign_margin_after_cost = args.target_units * margin_per_unit - args.campaign_cost
    rec, notes = recommendation(roi, margin_pct, net_contribution, break_even_total_units, args.target_units)

    return {
        "Campaign": args.campaign,
        "Client/Channel": args.client,
        "SKU": args.sku,
        "Baseline Units": args.baseline_units,
        "Target Units": args.target_units,
        "Incremental Units": incremental_units,
        "Unit Price": round(unit_price, 2),
        "Unit Cost": round(unit_cost, 2),
        "Margin/Unit": round(margin_per_unit, 2),
        "Margin % on Cost": percent(margin_pct),
        "Incremental Margin": round(incremental_margin, 2),
        "Campaign Cost": round(args.campaign_cost, 2),
        "Break-even Incremental Units": break_even_incremental_units,
        "Break-even Total Units": break_even_total_units,
        "Net Contribution": round(net_contribution, 2),
        "ROI": percent(roi),
        "Total Campaign Margin After Cost": round(total_campaign_margin_after_cost, 2),
        "Recommendation": rec,
        "Notes": notes,
    }


def write_outputs(row: dict[str, object], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "campaign_profitability.csv"
    md_path = output_dir / "campaign_profitability.md"

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)

    lines = [
        f"# Análisis de rentabilidad — {row['Campaign']}",
        "",
        "## Resumen",
        "",
        f"- Recomendación: {row['Recommendation']}.",
        f"- ROI: {row['ROI']}.",
        f"- Contribución neta: {money(float(row['Net Contribution']))}.",
        f"- Punto de equilibrio: {row['Break-even Total Units']} unidades totales.",
        f"- Riesgo/nota: {row['Notes']}",
        "",
        "## Detalle",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ]
    for key, value in row.items():
        lines.append(f"| {key} | {value} |")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"CSV: {csv_path}")
    print(f"Markdown: {md_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True)
    parser.add_argument("--client", required=True)
    parser.add_argument("--sku", required=True)
    parser.add_argument("--baseline-units", required=True, type=int)
    parser.add_argument("--target-units", required=True, type=int)
    parser.add_argument("--campaign-cost", required=True, type=float)
    parser.add_argument("--unit-price", type=float)
    parser.add_argument("--unit-cost", type=float)
    parser.add_argument("--output-dir", type=Path, default=Path(".tmp"))
    args = parser.parse_args()

    row = analyze(args)
    write_outputs(row, args.output_dir)


if __name__ == "__main__":
    main()
