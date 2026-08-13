"""Fetch Dominican Republic economic indicators from the World Bank API."""
import requests

WORLD_BANK_API = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
COUNTRY = "DOM"

INDICATORS = {
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",       # GDP growth (annual %)
    "inflation": "FP.CPI.TOTL.ZG",           # Inflation, consumer prices (annual %)
    "exchange_rate": "PA.NUS.FCRF",          # Official exchange rate (LCU per US$, period average)
}


def fetch_indicator(indicator_code: str, per_page: int = 100) -> list[dict]:
    """Fetch a single indicator's time series for the Dominican Republic."""
    url = WORLD_BANK_API.format(country=COUNTRY, indicator=indicator_code)
    params = {"format": "json", "per_page": per_page}
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    payload = response.json()

    if not isinstance(payload, list) or len(payload) < 2 or payload[1] is None:
        raise ValueError(f"Unexpected response for {indicator_code}: {payload}")

    records = payload[1]
    # Keep only entries with a non-null value, sorted by year ascending.
    cleaned = [
        {"year": int(r["date"]), "value": r["value"]}
        for r in records
        if r["value"] is not None
    ]
    cleaned.sort(key=lambda r: r["year"])
    return cleaned


def fetch_all() -> dict[str, list[dict]]:
    return {name: fetch_indicator(code) for name, code in INDICATORS.items()}


if __name__ == "__main__":
    data = fetch_all()
    for name, series in data.items():
        print(f"\n=== {name} ({INDICATORS[name]}) ===")
        print(f"{len(series)} data points, years {series[0]['year']}-{series[-1]['year']}")
        for point in series[-5:]:
            print(f"  {point['year']}: {point['value']}")
