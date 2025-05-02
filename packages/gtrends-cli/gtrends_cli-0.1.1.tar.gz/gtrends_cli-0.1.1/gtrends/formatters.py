"""Output formatting utilities."""

import json
import os
from pathlib import Path
from typing import Dict, Optional, Union

import pandas as pd
from rich.box import ROUNDED
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


def is_bat_available() -> bool:
    """Check if 'bat' is available in the system."""
    try:
        return os.system("which bat > /dev/null 2>&1") == 0
    except Exception:
        return False


def format_trending_searches(
    df: pd.DataFrame,
    title: str = "Trending Searches",
    count: int = 10,
    news_articles: Optional[Dict] = None,
) -> None:
    """Format and print trending searches using rich tables.

    Args:
        df: DataFrame containing trending searches
        title: Title for the table
        count: Number of results to show
        news_articles: Optional dictionary of news articles
    """
    if df.empty:
        console.print(Panel("No trending searches found", title=title))
        return

    # Limit to the requested number of results
    if len(df) > count:
        df = df.head(count)

    # Create a rich table
    table = Table(title=title, box=ROUNDED)
    table.add_column("#", justify="right", style="dim")
    table.add_column("Trending Search", justify="left", style="green")

    if "traffic" in df.columns and df["traffic"].any():
        table.add_column("Traffic", justify="right")

    # Add rows
    for _, row in df.iterrows():
        if "traffic" in df.columns and row["traffic"]:
            table.add_row(str(row["rank"]), row["title"], str(row["traffic"]))
        else:
            table.add_row(str(row["rank"]), row["title"])

    console.print(table)

    # Display news articles if provided
    if news_articles and len(news_articles) > 0:
        console.print("\n[bold]Related News Articles:[/bold]")

        for topic, articles in news_articles.items():
            if articles:
                console.print(f"\n[bold green]{topic}[/bold green]")

                for i, article in enumerate(articles[:3], 1):  # Limit to 3 articles per topic
                    console.print(f"  {i}. [blue]{article['title']}[/blue]")
                    source_info = f"{article['source']}"
                    if "time_ago" in article and article["time_ago"]:
                        source_info += f" • {article['time_ago']}"
                    console.print(f"     [dim]{source_info}[/dim]")
                    console.print(f"     {article['url']}\n")


def format_related_data(
    data: Dict[str, pd.DataFrame], data_type: str = "topics", count: int = 10
) -> None:
    """Format and print related topics or queries.

    Args:
        data: Dictionary with 'top' and 'rising' DataFrames
        data_type: Type of data ("topics" or "queries")
        count: Number of results to show
    """
    if not data:
        console.print(Panel(f"No related {data_type} found", title=f"Related {data_type.title()}"))
        return

    # Process top related data
    if "top" in data and not data["top"].empty:
        top_df = data["top"].head(count)

        table = Table(title=f"Top Related {data_type.title()}", box=ROUNDED)
        table.add_column("#", justify="right", style="dim")
        table.add_column(f"{data_type.title()[:-1]}", style="green")
        table.add_column("Value", justify="right")

        # Determine column names based on data structure
        title_col = "topic_title" if "topic_title" in top_df.columns else "query"
        value_col = "value"

        # Add rows
        for i, (_, row) in enumerate(top_df.iterrows(), 1):
            title = str(row[title_col]) if title_col in row else str(row[0])
            value = str(row[value_col]) if value_col in row else str(row[1])

            table.add_row(str(i), title, value)

        console.print(table)

    # Process rising related data
    if "rising" in data and not data["rising"].empty:
        rising_df = data["rising"].head(count)

        table = Table(title=f"Rising Related {data_type.title()}", box=ROUNDED)
        table.add_column("#", justify="right", style="dim")
        table.add_column(f"{data_type.title()[:-1]}", style="green")
        table.add_column("% Increase", justify="right")

        # Determine column names based on data structure
        title_col = "topic_title" if "topic_title" in rising_df.columns else "query"
        value_col = "value"

        # Add rows
        for i, (_, row) in enumerate(rising_df.iterrows(), 1):
            title = str(row[title_col]) if title_col in row else str(row[0])
            value = str(row[value_col]) if value_col in row else str(row[1])

            table.add_row(str(i), title, value)

        console.print(table)


def format_interest_by_region(
    df: pd.DataFrame, title: str = "Interest by Region", count: int = 10
) -> None:
    """Format and print interest by region data.

    Args:
        df: DataFrame containing interest by region
        title: Title for the table
        count: Number of results to show
    """
    if df.empty:
        console.print(Panel("No geographic data found", title=title))
        return

    # Limit to the requested number of rows
    df_top = df.head(count)

    # Create a rich table
    table = Table(title=title, box=ROUNDED)
    table.add_column("Region", style="green")

    # Add column for each query
    for col in df.columns:
        table.add_column(col, justify="right")

    # Add rows
    for region, row in df_top.iterrows():
        values = [f"{v:.0f}" for v in row]
        table.add_row(str(region), *values)

    console.print(table)


def format_interest_over_time(
    df: pd.DataFrame, title: str = "Interest Over Time", export_path: Optional[Path] = None
) -> None:
    """Format time series data and optionally create a plot.

    Args:
        df: DataFrame with time series data
        title: Title for the output
        export_path: Optional path to export visualization
    """
    if df.empty:
        console.print(Panel("No time series data found", title=title))
        return

    # Display summary in the console
    console.print(f"[bold]{title}[/bold]\n")

    # Calculate stats for each column
    for col in df.columns:
        if col == "date":
            continue

        avg = df[col].mean()
        max_val = df[col].max()
        max_date = df.loc[df[col].idxmax(), "date"] if "date" in df.columns else None

        console.print(f"[green]{col}[/green]:")
        console.print(f"  Average interest: {avg:.1f}")
        console.print(f"  Peak interest: {max_val:.0f}")

        if max_date:
            console.print(f"  Peak date: {max_date}\n")
        else:
            console.print("")

    # Create a visualization if requested
    if export_path:
        try:
            import matplotlib.pyplot as plt

            # Check if 'date' column exists
            if "date" in df.columns:
                df.set_index("date", inplace=True)

            # Create plot
            plt.figure(figsize=(12, 6))
            for col in df.columns:
                plt.plot(df.index, df[col], label=col)

            plt.title(title)
            plt.legend()
            plt.grid(True, alpha=0.3)

            # Save plot
            export_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(export_path)

            console.print(f"[bold]Visualization saved to:[/bold] {export_path}")

        except ImportError:
            console.print(
                "Matplotlib is required for visualizations. Install with 'pip install matplotlib'."
            )
        except Exception as e:
            console.print(f"[red]Error creating visualization: {str(e)}[/red]")


def export_to_file(
    data: Union[pd.DataFrame, Dict[str, pd.DataFrame]],
    file_path: Path,
    format: str = "csv",
    news_articles: Optional[Dict] = None,
) -> bool:
    """Export data to a file.

    Args:
        data: DataFrame or dictionary of DataFrames to export
        file_path: Path to save the file
        format: Export format (csv, json, xlsx)
        news_articles: Optional dictionary of news articles to include

    Returns:
        True if export successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # If we have a trending search DataFrame and news articles, enhance the export
        if news_articles and isinstance(data, pd.DataFrame) and "keyword" in data.columns:
            export_data = data.copy()

            # Add news as separate files or combine into the main export
            if format == "json":
                # Clean up the data for the trends
                trends_json = json.loads(export_data.to_json(orient="records"))

                # Clean up news article data
                cleaned_news = {}
                for topic, articles in news_articles.items():
                    cleaned_articles = []
                    for article in articles:
                        # Clean article data
                        title = article["title"]
                        source = article["source"] if article["source"] else "Unknown Source"
                        # Filter out picture URLs
                        url = article["url"] if not article["url"].startswith("Picture") else ""

                        cleaned_articles.append(
                            {
                                "title": title,
                                "source": source,
                                "url": url,
                                "time_ago": article["time_ago"] if article["time_ago"] else "",
                            }
                        )
                    cleaned_news[topic] = cleaned_articles

                result = {"trends": trends_json, "news": cleaned_news}

                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)

                console.print(f"[green]Data exported to {file_path}[/green]")
                return True
            elif format == "csv":
                # Export trends to main CSV
                export_data.to_csv(file_path, index=False)

                # Export news to separate CSV
                news_file = file_path.with_stem(f"{file_path.stem}_news")

                # Create a flat structure for news
                news_rows = []
                for topic, articles in news_articles.items():
                    for article in articles:
                        title = article["title"]
                        source = article["source"] if article["source"] else "Unknown Source"
                        url = article["url"] if not article["url"].startswith("Picture") else ""

                        news_rows.append(
                            {
                                "topic": topic,
                                "title": title,
                                "source": source,
                                "url": url,
                                "time_ago": article["time_ago"] if article["time_ago"] else "",
                            }
                        )

                if news_rows:
                    pd.DataFrame(news_rows).to_csv(news_file.with_suffix(".csv"), index=False)

                console.print(f"[green]Data exported to {file_path}[/green]")
                return True

        # Handle regular DataFrames or dictionaries
        if isinstance(data, dict):
            # Create a combined DataFrame or export multiple files
            if format == "json":
                result = {}
                for key, df in data.items():
                    if df is not None and not df.empty:
                        result[key] = json.loads(df.to_json(orient="records"))
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
            else:
                # For CSV and Excel, we'll create separate files
                for key, df in data.items():
                    if df is not None and not df.empty:
                        part_path = file_path.with_stem(f"{file_path.stem}_{key}")
                        if format == "csv":
                            df.to_csv(part_path, index=False)
                        elif format == "xlsx":
                            df.to_excel(part_path, index=False)
        else:
            # Single DataFrame export
            if format == "csv":
                data.to_csv(file_path, index=False)
            elif format == "json":
                # Ensure UTF-8 encoding for non-ASCII characters
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(data.to_json(orient="records", force_ascii=False, indent=2))
            elif format == "xlsx":
                data.to_excel(file_path, index=False)

        console.print(f"[green]Data exported to {file_path}[/green]")
        return True

    except Exception as e:
        console.print(f"[red]Error exporting data: {str(e)}[/red]")
        return False


def with_spinner(message: str):
    """Decorator to show a spinner while executing a function.

    Args:
        message: Message to display with spinner
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            with Progress(
                SpinnerColumn(), TextColumn(f"[bold green]{message}"), transient=True
            ) as progress:
                progress.add_task("", total=None)
                return func(*args, **kwargs)

        return wrapper

    return decorator
