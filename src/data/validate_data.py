from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

FX_START = date(2010, 1, 1)
CRYPTO_START = date(2018, 1, 1)
END_TARGET = date(2024, 12, 31)
END_TOLERANCE_DAYS = 7

FX_EXTREME_DATES = {
    date(2015, 1, 15),  # SNB peg removal
    date(2016, 10, 7),  # Brexit flash crash
    date(2019, 1, 3),  # JPY flash crash
}
CRYPTO_EXTREME_DATES = {
    date(2020, 3, 12),  # COVID crash
    date(2021, 5, 19),  # May 2021 crash
    date(2022, 11, 8),  # FTX collapse
}

SIZE_MIN_PER_YEAR_BYTES = 100 * 1024 * 1024
SIZE_MAX_PER_YEAR_BYTES = 500 * 1024 * 1024

FX_DIR = Path("data/fx/raw")
CRYPTO_DIR = Path("data/crypto/raw")


@dataclass
class FileReport:
    path: Path
    asset_type: str
    pass_date_completeness: bool
    pass_extremes: bool
    pass_quality: bool
    pass_size: bool
    timezone_inference: str
    failures: list[str]


@dataclass
class FileStats:
    start_date: Optional[date]
    end_date: Optional[date]
    date_set: set[date]
    missing_extreme_dates: list[date]
    gap_descriptions: list[str]
    negative_price_rows: int
    bad_high_low_rows: int
    bad_close_range_rows: int
    nan_price_rows: int
    nonzero_volume_seen: bool
    size_bytes: int
    size_per_year_bytes: Optional[float]
    timezone_inference: str


@dataclass
class ValidationResult:
    reports: list[FileReport]
    all_passed: bool


def has_required_csv_inputs() -> tuple[bool, str | None]:
    """Verify both raw-data directories contain at least one CSV file."""
    if not list_csv_files(FX_DIR) or not list_csv_files(CRYPTO_DIR):
        return False, "ERROR: No CSV files found. Downloads must have failed."
    return True, None


def list_csv_files(directory: Path) -> list[Path]:
    """Return sorted CSV files in the target directory."""
    if not directory.exists():
        return []
    return sorted(path for path in directory.glob("*.csv") if path.is_file())


def infer_asset_type(path: Path) -> str:
    """Infer asset type based on the file location."""
    parts = {part.lower() for part in path.parts}
    if "fx" in parts:
        return "fx"
    if "crypto" in parts:
        return "crypto"
    return "unknown"


def find_missing_extreme_dates(dates: Iterable[date], required: set[date]) -> list[date]:
    """Return required dates that are missing from the dataset."""
    date_set = set(dates)
    missing = sorted(required - date_set)
    return missing


def describe_date_gaps(sorted_dates: list[date], allow_weekends: bool) -> list[str]:
    """Describe gaps larger than a day, with optional weekend allowance."""
    gaps: list[str] = []
    for prev, nxt in zip(sorted_dates, sorted_dates[1:]):
        delta = (nxt - prev).days
        if delta <= 1:
            continue
        if allow_weekends and prev.weekday() == 4 and nxt.weekday() == 0 and delta == 3:
            continue
        gaps.append(f"{prev} -> {nxt} ({delta} days)")
    return gaps


def infer_timezone(min_time_seconds_by_day: dict[date, int]) -> str:
    """Infer timezone heuristically from the minimum timestamp in each day."""
    if not min_time_seconds_by_day:
        return "unknown (no data)"
    counts = Counter(min_time_seconds_by_day.values())
    most_common_seconds, _ = counts.most_common(1)[0]

    def within(value: int, target: int, tolerance_minutes: int = 60) -> bool:
        return abs(value - target) <= tolerance_minutes * 60

    if within(most_common_seconds, 0):
        return "UTC (inferred from day start at ~00:00)"
    if within(most_common_seconds, 17 * 3600):
        return "America/New_York (inferred from day start at ~17:00)"
    hours = most_common_seconds // 3600
    minutes = (most_common_seconds % 3600) // 60
    return f"unknown (day starts around {hours:02d}:{minutes:02d})"


def check_date_bounds(
    start: Optional[date], end: Optional[date], expected_start: date
) -> tuple[bool, list[str]]:
    """Check that the start and end dates are within expected bounds."""
    failures: list[str] = []
    if start is None:
        failures.append("missing start date")
    elif start != expected_start:
        failures.append(f"start date {start} != {expected_start}")
    if end is None:
        failures.append("missing end date")
    else:
        min_end = END_TARGET - timedelta(days=END_TOLERANCE_DAYS)
        max_end = END_TARGET + timedelta(days=END_TOLERANCE_DAYS)
        if not (min_end <= end <= max_end):
            failures.append(f"end date {end} not within {min_end}..{max_end}")
    return len(failures) == 0, failures


def compute_size_per_year(size_bytes: int, years: int) -> Optional[float]:
    """Compute average size per year, returning None for invalid inputs."""
    if years <= 0:
        return None
    return size_bytes / years


def analyze_file(path: Path) -> FileStats:
    """Analyze a CSV file and return computed statistics."""
    header = pd.read_csv(path, nrows=0)
    columns = list(header.columns)

    if "datetime" in columns:
        date_columns = ["datetime"]
    elif "date" in columns and "time" in columns:
        date_columns = ["date", "time"]
    else:
        raise ValueError(f"Unable to find datetime columns in {path}")

    price_columns = ["open", "high", "low", "close", "volume"]
    usecols = list({*date_columns, *price_columns} & set(columns))

    date_set: set[date] = set()
    min_time_seconds_by_day: dict[date, int] = {}

    start_date: Optional[date] = None
    end_date: Optional[date] = None

    negative_price_rows = 0
    bad_high_low_rows = 0
    bad_close_range_rows = 0
    nan_price_rows = 0
    nonzero_volume_seen = False

    for chunk in pd.read_csv(path, usecols=usecols, chunksize=500_000):
        if "datetime" in chunk.columns:
            dt = pd.to_datetime(chunk["datetime"], errors="coerce")
        else:
            date_str = chunk["date"].astype(str).str.zfill(8)
            time_str = chunk["time"].astype(str).str.zfill(6)
            dt = pd.to_datetime(date_str + time_str, format="%Y%m%d%H%M%S", errors="coerce")

        valid_dt = dt.dropna()
        if not valid_dt.empty:
            days = valid_dt.dt.date
            date_set.update(days)

            day_floor = valid_dt.dt.floor("D")
            time_seconds = valid_dt.dt.hour * 3600 + valid_dt.dt.minute * 60 + valid_dt.dt.second
            day_min = pd.Series(time_seconds).groupby(day_floor.dt.date).min()
            for day, seconds in day_min.items():
                current = min_time_seconds_by_day.get(day)
                if current is None or seconds < current:
                    min_time_seconds_by_day[day] = int(seconds)

            chunk_start = min(days)
            chunk_end = max(days)
            if start_date is None or chunk_start < start_date:
                start_date = chunk_start
            if end_date is None or chunk_end > end_date:
                end_date = chunk_end

        if not set(price_columns).issubset(chunk.columns):
            raise ValueError(f"Missing price columns in {path}")

        numeric = chunk[price_columns].apply(pd.to_numeric, errors="coerce")
        nan_price_rows += int(numeric[["open", "high", "low", "close"]].isna().any(axis=1).sum())
        negative_price_rows += int((numeric[["open", "high", "low", "close"]] < 0).any(axis=1).sum())
        bad_high_low_rows += int((numeric["high"] < numeric["low"]).sum())
        bad_close_range_rows += int(
            (~numeric["close"].between(numeric["low"], numeric["high"], inclusive="both")).sum()
        )
        if (numeric["volume"] > 0).any():
            nonzero_volume_seen = True

    timezone_inference = infer_timezone(min_time_seconds_by_day)

    size_bytes = path.stat().st_size

    return FileStats(
        start_date=start_date,
        end_date=end_date,
        date_set=date_set,
        missing_extreme_dates=[],
        gap_descriptions=[],
        negative_price_rows=negative_price_rows,
        bad_high_low_rows=bad_high_low_rows,
        bad_close_range_rows=bad_close_range_rows,
        nan_price_rows=nan_price_rows,
        nonzero_volume_seen=nonzero_volume_seen,
        size_bytes=size_bytes,
        size_per_year_bytes=None,
        timezone_inference=timezone_inference,
    )


def validate_file(path: Path) -> tuple[FileReport, FileStats]:
    """Validate a CSV file and return a report and stats."""
    asset_type = infer_asset_type(path)
    stats = analyze_file(path)

    if asset_type == "fx":
        expected_start = FX_START
        extreme_dates = FX_EXTREME_DATES
        allow_weekends = True
        years = 2024 - 2010 + 1
    elif asset_type == "crypto":
        expected_start = CRYPTO_START
        extreme_dates = CRYPTO_EXTREME_DATES
        allow_weekends = False
        years = 2024 - 2018 + 1
    else:
        expected_start = FX_START
        extreme_dates = set()
        allow_weekends = False
        years = 0

    sorted_dates = sorted(stats.date_set)
    if not sorted_dates:
        gap_failures = ["missing date data"]
    else:
        gap_failures = describe_date_gaps(sorted_dates, allow_weekends)

    missing_extremes = find_missing_extreme_dates(sorted_dates, extreme_dates)

    pass_date_bounds, date_bound_failures = check_date_bounds(
        stats.start_date, stats.end_date, expected_start
    )
    pass_date_completeness = pass_date_bounds and not gap_failures

    pass_extremes = len(missing_extremes) == 0

    quality_failures = []
    if stats.nan_price_rows > 0:
        quality_failures.append(f"{stats.nan_price_rows} rows with NaN prices")
    if stats.negative_price_rows > 0:
        quality_failures.append(f"{stats.negative_price_rows} rows with negative prices")
    if stats.bad_high_low_rows > 0:
        quality_failures.append(f"{stats.bad_high_low_rows} rows with high < low")
    if stats.bad_close_range_rows > 0:
        quality_failures.append(f"{stats.bad_close_range_rows} rows with close outside [low, high]")
    if not stats.nonzero_volume_seen:
        quality_failures.append("volume is zero for all rows")
    pass_quality = len(quality_failures) == 0

    size_per_year = compute_size_per_year(stats.size_bytes, years)
    stats.size_per_year_bytes = size_per_year
    size_failures = []
    if size_per_year is None:
        size_failures.append("unable to compute size per year")
    else:
        if size_per_year < SIZE_MIN_PER_YEAR_BYTES or size_per_year > SIZE_MAX_PER_YEAR_BYTES:
            size_failures.append(
                f"size per year {size_per_year / (1024 * 1024):.1f}MB not in 100-500MB"
            )
    pass_size = len(size_failures) == 0

    failures: list[str] = []
    if not pass_date_completeness:
        failures.extend(date_bound_failures)
        failures.extend(gap_failures)
    if not pass_extremes:
        failures.append(f"missing extremes: {', '.join(str(d) for d in missing_extremes)}")
    if not pass_quality:
        failures.extend(quality_failures)
    if not pass_size:
        failures.extend(size_failures)

    report = FileReport(
        path=path,
        asset_type=asset_type,
        pass_date_completeness=pass_date_completeness,
        pass_extremes=pass_extremes,
        pass_quality=pass_quality,
        pass_size=pass_size,
        timezone_inference=stats.timezone_inference,
        failures=failures,
    )
    stats.missing_extreme_dates = missing_extremes
    stats.gap_descriptions = gap_failures
    return report, stats


def render_report(report: FileReport, stats: FileStats) -> None:
    """Print a formatted report for a single file."""
    print(f"\nFile: {report.path}")
    print(f"Asset type: {report.asset_type}")
    if stats.start_date:
        print(f"Start date: {stats.start_date}")
    else:
        print("Start date: missing")
    if stats.end_date:
        print(f"End date: {stats.end_date}")
    else:
        print("End date: missing")
    print(
        f"File size: {stats.size_bytes / (1024 * 1024):.1f}MB"
        + (
            f" ({stats.size_per_year_bytes / (1024 * 1024):.1f}MB per year)"
            if stats.size_per_year_bytes is not None
            else ""
        )
    )
    print(f"Timezone inference: {report.timezone_inference}")

    print(f"Date completeness: {'PASS' if report.pass_date_completeness else 'FAIL'}")
    if stats.gap_descriptions:
        print("  Gaps:")
        for gap in stats.gap_descriptions[:10]:
            print(f"   - {gap}")
        if len(stats.gap_descriptions) > 10:
            print(f"   - ... {len(stats.gap_descriptions) - 10} more")

    print(f"Extreme events present: {'PASS' if report.pass_extremes else 'FAIL'}")
    if stats.missing_extreme_dates:
        missing_str = ", ".join(str(d) for d in stats.missing_extreme_dates)
        print(f"  Missing: {missing_str}")

    print(f"Data quality: {'PASS' if report.pass_quality else 'FAIL'}")
    if stats.nan_price_rows > 0:
        print(f"  NaN price rows: {stats.nan_price_rows}")
    if stats.negative_price_rows > 0:
        print(f"  Negative price rows: {stats.negative_price_rows}")
    if stats.bad_high_low_rows > 0:
        print(f"  High < Low rows: {stats.bad_high_low_rows}")
    if stats.bad_close_range_rows > 0:
        print(f"  Close outside [Low, High] rows: {stats.bad_close_range_rows}")
    if not stats.nonzero_volume_seen:
        print("  Volume never positive")

    print(f"File size check: {'PASS' if report.pass_size else 'FAIL'}")
    if report.failures:
        print("Failures:")
        for failure in report.failures:
            print(f" - {failure}")


def validate_all() -> ValidationResult:
    """Validate all FX and crypto CSVs under the data directories."""
    inputs_ok, error_message = has_required_csv_inputs()
    if not inputs_ok:
        print(error_message)
        return ValidationResult(reports=[], all_passed=False)

    files = list_csv_files(FX_DIR) + list_csv_files(CRYPTO_DIR)
    reports: list[FileReport] = []
    all_passed = True

    for path in files:
        report, stats = validate_file(path)
        render_report(report, stats)
        reports.append(report)
        if not (
            report.pass_date_completeness
            and report.pass_extremes
            and report.pass_quality
            and report.pass_size
        ):
            all_passed = False

    return ValidationResult(reports=reports, all_passed=all_passed)


def main() -> None:
    """CLI entry point."""
    result = validate_all()
    if result.all_passed:
        print("\nOverall result: PASS")
        sys.exit(0)
    print("\nOverall result: FAIL")
    sys.exit(1)


if __name__ == "__main__":
    main()
