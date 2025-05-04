def print_stats(stats: dict, title: str = "Stats") -> None:
    print(f"\n=== {title.upper()} ===")
    for key, value in stats.items():
        label = key.replace("_", " ").title()
        print(f"{label:<15}: {value}")
    print("=" * 30)
