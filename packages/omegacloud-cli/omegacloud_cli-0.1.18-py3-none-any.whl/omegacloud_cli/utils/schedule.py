from typing import List

# Mapping of special cron strings to their equivalent cron expressions
SPECIAL_CRON_MAP = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
    "@reboot": None,  # Not supported in Celery
}

# Mapping of named days to their numeric values (0-6 for cron, 1-7 for Celery)
DAY_NAMES = {
    "sun": "7",
    "sunday": "7",
    "mon": "1",
    "monday": "1",
    "tue": "2",
    "tuesday": "2",
    "wed": "3",
    "wednesday": "3",
    "thu": "4",
    "thursday": "4",
    "fri": "5",
    "friday": "5",
    "sat": "6",
    "saturday": "6",
}


def cron_to_celery_cron(cron_expr: str) -> List[str]:
    """
    Convert standard cron expression to Celery crontab format.

    Handles the following conversions:
    - Special strings (@yearly, @monthly, @weekly, etc.)
    - Named days of week (sun, mon, tue, etc.)
    - Day of week: 0-6 (Sun-Sat) -> 1-7 (Mon-Sun)
    - Ranges and steps
    - Lists of values
    - Special characters (*, ?, L, W, #)

    Args:
        cron_expr (str): Standard cron expression (minute hour day month day_of_week)
                        or special string (@yearly, @monthly, etc.)

    Returns:
        list: List of normalized cron parts for Celery crontab

    Raises:
        ValueError: If the cron expression is invalid or @reboot is used
    """
    # Handle special cron strings
    if cron_expr in SPECIAL_CRON_MAP:
        if cron_expr == "@reboot":
            raise ValueError("@reboot is not supported")
        cron_expr = SPECIAL_CRON_MAP[cron_expr]

    parts = cron_expr.strip().split()
    if len(parts) != 5:
        raise ValueError("Invalid cron format, must have 5 fields")

    def normalize_range(field: str, max_val: int) -> str:
        """Normalize a single cron field to Celery format."""
        if field == "*":
            return field
        if field == "?":
            return "*"

        # Handle ranges with steps
        if "/" in field:
            base, step = field.split("/")
            step = int(step)

            # Handle ranges with steps (e.g., "0-20/2")
            if "-" in base:
                start, end = map(int, base.split("-"))
                return ",".join(str(i) for i in range(start, end + 1, step))
            # Handle simple steps (e.g., "*/2")
            elif base == "*":
                return field
            # Handle start with step (e.g., "5/2")
            else:
                start = int(base)
                return ",".join(str(i) for i in range(start, max_val + 1, step))

        # Handle lists
        if "," in field:
            values = field.split(",")
            normalized = []
            for value in values:
                if "-" in value:
                    start, end = map(int, value.split("-"))
                    normalized.extend(str(i) for i in range(start, end + 1))
                else:
                    normalized.append(value)
            return ",".join(normalized)

        # Handle ranges
        if "-" in field:
            start, end = map(int, field.split("-"))
            return ",".join(str(i) for i in range(start, end + 1))

        return field

    minute, hour, day_of_month, month_of_year, day_of_week = parts

    # Normalize each field
    minute = normalize_range(minute, 59)
    hour = normalize_range(hour, 23)
    day_of_month = normalize_range(day_of_month, 31)
    month_of_year = normalize_range(month_of_year, 12)

    # Special handling for day of week
    day_of_week = day_of_week.lower()
    if day_of_week in DAY_NAMES:
        day_of_week = DAY_NAMES[day_of_week]
    elif day_of_week == "0":
        day_of_week = "7"
    elif day_of_week == "?":
        day_of_week = "*"
    elif "," in day_of_week:
        # Convert all Sunday (0) to 7 in lists and handle named days
        values = day_of_week.split(",")
        normalized = []
        for value in values:
            value = value.lower()
            if value in DAY_NAMES:
                normalized.append(DAY_NAMES[value])
            elif value == "0":
                normalized.append("7")
            else:
                normalized.append(value)
        day_of_week = ",".join(normalized)
    elif "-" in day_of_week:
        # Handle ranges in day of week
        start, end = day_of_week.split("-")
        start = DAY_NAMES.get(start.lower(), start)
        end = DAY_NAMES.get(end.lower(), end)
        start = int(start)
        end = int(end)
        if start == 0:
            start = 7
        if end == 0:
            end = 7
        day_of_week = ",".join(str(i) for i in range(start, end + 1))
    else:
        day_of_week = normalize_range(day_of_week, 7)

    return [
        minute,
        hour,
        day_of_month,
        month_of_year,
        day_of_week,
    ]
