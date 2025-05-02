"""Command-line interface for Google Trends tool."""

import sys
from typing import Optional

import click
from rich.console import Console

from gtrends.config import (
    DEFAULT_CATEGORY,
    DEFAULT_SUGGESTIONS_COUNT,
    DEFAULT_TIMEFRAME,
    BatchPeriod,
)
from gtrends.content_suggestions import ContentSuggester
from gtrends.formatters import (
    export_to_file,
    format_interest_by_region,
    format_interest_over_time,
    format_related_data,
    format_trending_searches,
    with_spinner,
)
from gtrends.trends_api import TrendsClient
from gtrends.utils import (
    format_region_name,
    parse_timeframe,
    validate_export_path,
    validate_region_code,
)

console = Console()


@click.group()
@click.version_option(version="0.0.1")
def cli():
    """Google Trends CLI - Fetch trending topics & analyze search interests for content creators."""
    pass


@cli.command()
@click.option(
    "--region", "-r", help="Region code (e.g., US, GB, AE). Auto-detects if not specified."
)
@click.option(
    "--count",
    "-n",
    type=int,
    default=DEFAULT_SUGGESTIONS_COUNT,
    help=f"Number of results to display. Default: {DEFAULT_SUGGESTIONS_COUNT}",
)
@click.option("--with-news", "-w", is_flag=True, help="Include related news articles")
@click.option("--export", "-e", is_flag=True, help="Export results to file")
@click.option("--export-path", type=str, help="Directory to save exported data")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "xlsx"]),
    default="csv",
    help="Export format",
)
def trending(
    region: Optional[str],
    count: int,
    with_news: bool,
    export: bool,
    export_path: Optional[str],
    format: str,
):
    """Show current trending searches on Google."""
    try:
        client = TrendsClient()
        region_code = validate_region_code(region) if region else None

        if with_news:
            with_spinner("Fetching trending searches with news articles...")(lambda: None)()
            trending_df, news_articles = client.get_trending_searches_with_articles(
                region=region_code, limit=count
            )
        else:
            with_spinner("Fetching trending searches...")(lambda: None)()
            trending_df = client.get_trending_searches(region=region_code, limit=count)
            news_articles = None

        # Display results
        region_display = region_code if region_code else client.get_current_region()
        region_name = format_region_name(region_display)

        format_trending_searches(
            trending_df,
            title=f"Trending Searches - {region_name}",
            count=count,
            news_articles=news_articles,
        )

        # Export if requested
        if export:
            export_dir = validate_export_path(export_path)
            export_file = export_dir / f"trending_searches_{region_display}.{format}"
            export_to_file(trending_df, export_file, format)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@cli.command()
@click.argument("query", type=str)
@click.option(
    "--region", "-r", help="Region code (e.g., US, GB, AE). Auto-detects if not specified."
)
@click.option(
    "--timeframe",
    "-t",
    default=DEFAULT_TIMEFRAME,
    help=f"Timeframe for data (e.g., 'today 1-d', 'today 3-m'). Default: {DEFAULT_TIMEFRAME}",
)
@click.option(
    "--category",
    type=str,
    default=DEFAULT_CATEGORY,
    help=f"Category ID to filter results. Default: {DEFAULT_CATEGORY} (All)",
)
@click.option(
    "--count",
    "-n",
    type=int,
    default=DEFAULT_SUGGESTIONS_COUNT,
    help=f"Number of results to display. Default: {DEFAULT_SUGGESTIONS_COUNT}",
)
@click.option("--export", "-e", is_flag=True, help="Export results to file")
@click.option("--export-path", type=str, help="Directory to save exported data")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "xlsx"]),
    default="csv",
    help="Export format",
)
def related(
    query: str,
    region: Optional[str],
    timeframe: str,
    category: str,
    count: int,
    export: bool,
    export_path: Optional[str],
    format: str,
):
    """Show topics and queries related to a search term."""
    try:
        client = TrendsClient()
        region_code = validate_region_code(region) if region else None
        timeframe_parsed = parse_timeframe(timeframe)

        # Get related topics
        with_spinner(f"Fetching related topics for '{query}'...")(lambda: None)()
        related_topics = client.get_related_topics(
            query=query, region=region_code, timeframe=timeframe_parsed, category=category
        )

        # Get related queries
        with_spinner(f"Fetching related queries for '{query}'...")(lambda: None)()
        related_queries = client.get_related_queries(
            query=query, region=region_code, timeframe=timeframe_parsed, category=category
        )

        # Display results
        region_display = region_code if region_code else client.get_current_region()
        region_name = format_region_name(region_display)

        console.print(
            f"[bold]Related data for '{query}' in {region_name} over {timeframe_parsed}[/bold]\n"
        )

        format_related_data(related_topics, data_type="topics", count=count)
        format_related_data(related_queries, data_type="queries", count=count)

        # Export if requested
        if export:
            export_dir = validate_export_path(export_path)

            # Export topics
            topics_file = export_dir / f"related_topics_{query}_{region_display}.{format}"
            export_to_file(related_topics, topics_file, format)

            # Export queries
            queries_file = export_dir / f"related_queries_{query}_{region_display}.{format}"
            export_to_file(related_queries, queries_file, format)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@cli.command()
@click.option(
    "--category",
    "-c",
    default="books",
    help="Content category (books, news, arts, fiction, culture)",
)
@click.option(
    "--region", "-r", help="Region code (e.g., US, GB, AE). Auto-detects if not specified."
)
@click.option(
    "--timeframe", "-t", default="now 7-d", help="Timeframe for data (e.g., 'now 7-d', 'today 1-m')"
)
@click.option(
    "--count",
    "-n",
    type=int,
    default=DEFAULT_SUGGESTIONS_COUNT,
    help=f"Number of results to display. Default: {DEFAULT_SUGGESTIONS_COUNT}",
)
@click.option("--export", "-e", is_flag=True, help="Export results to file")
@click.option("--export-path", type=str, help="Directory to save exported data")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "xlsx"]),
    default="csv",
    help="Export format",
)
def suggest_topics(
    category: str,
    region: Optional[str],
    timeframe: str,
    count: int,
    export: bool,
    export_path: Optional[str],
    format: str,
):
    """Suggest trending topics for content creators."""
    try:
        client = TrendsClient()
        suggester = ContentSuggester(client)

        region_code = validate_region_code(region) if region else None
        timeframe_parsed = parse_timeframe(timeframe)
        with_spinner(f"Finding content suggestions in {category} category...")(lambda: None)()
        suggestions_df = suggester.suggest_topics(
            category=category, region=region_code, timeframe=timeframe_parsed, count=count
        )

        # Display results
        if suggestions_df.empty:
            console.print("[yellow]No content suggestions found for the given parameters.[/yellow]")
            return

        region_display = region_code if region_code else client.get_current_region()
        region_name = format_region_name(region_display)

        # Create a rich table for display
        from rich.table import Table

        table = Table(title=f"Content Suggestions - {category.title()} in {region_name}")
        table.add_column("#", justify="right", style="dim")
        table.add_column("Topic", style="green")
        table.add_column("Relevance", justify="right")
        table.add_column("Source", style="blue")
        table.add_column("Trending", style="yellow")

        for i, (_, row) in enumerate(suggestions_df.iterrows(), 1):
            table.add_row(
                str(i),
                row["topic"],
                str(int(row["relevance_score"])),
                row["source"],
                "↑ Rising" if row["rising"] else "✓ Stable",
            )

        console.print(table)

        # Export if requested
        if export:
            export_dir = validate_export_path(export_path)
            export_file = export_dir / f"content_suggestions_{category}_{region_display}.{format}"
            export_to_file(suggestions_df, export_file, format)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@cli.command()
@click.argument("topics", nargs=-1, required=True)
@click.option(
    "--region", "-r", help="Region code (e.g., US, GB, AE). Auto-detects if not specified."
)
@click.option(
    "--timeframe",
    "-t",
    default="today 3-m",
    help="Timeframe for data (e.g., 'today 3-m', 'today 12-m')",
)
@click.option(
    "--category",
    type=str,
    default=DEFAULT_CATEGORY,
    help=f"Category ID to filter results. Default: {DEFAULT_CATEGORY} (All)",
)
@click.option("--export", "-e", is_flag=True, help="Export results to file")
@click.option("--export-path", type=str, help="Directory to save exported data")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "xlsx"]),
    default="csv",
    help="Export format",
)
@click.option("--visualize", "-v", is_flag=True, help="Generate visualization")
def compare(
    topics,
    region: Optional[str],
    timeframe: str,
    category: str,
    export: bool,
    export_path: Optional[str],
    format: str,
    visualize: bool,
):
    """Compare interest over time for multiple topics (max 5)."""
    try:
        if not topics:
            console.print(
                "[bold red]Error:[/bold red] Please provide at least one topic to compare."
            )
            return

        if len(topics) > 5:
            console.print(
                "[bold yellow]Warning:[/bold yellow] Google Trends supports comparing max 5 topics."
            )
            topics = topics[:5]

        client = TrendsClient()

        region_code = validate_region_code(region) if region else None
        timeframe_parsed = parse_timeframe(timeframe)

        with_spinner(f"Comparing interest for topics: {', '.join(topics)}...")(lambda: None)()
        interest_df = client.get_interest_over_time(
            queries=list(topics), region=region_code, timeframe=timeframe_parsed, category=category
        )

        # Display results
        if interest_df.empty:
            console.print("[yellow]No comparison data found for the given topics.[/yellow]")
            return

        region_display = region_code if region_code else client.get_current_region()
        region_name = format_region_name(region_display)

        # Create visualization if requested
        viz_path = None
        if visualize and export:
            export_dir = validate_export_path(export_path)
            viz_path = export_dir / f"topic_comparison_{region_display}.png"

        # Display formatted results
        format_interest_over_time(
            interest_df,
            title=f"Interest Comparison - {region_name} over {timeframe_parsed}",
            export_path=viz_path if visualize else None,
        )

        # Export if requested
        if export:
            export_dir = validate_export_path(export_path)
            export_file = export_dir / f"topic_comparison_{region_display}.{format}"
            export_to_file(interest_df, export_file, format)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@cli.command()
@click.option(
    "--region", "-r", help="Region code (e.g., US, GB, AE). Auto-detects if not specified."
)
@click.option(
    "--timeframe",
    "-t",
    default="today 1-m",
    help="Timeframe for data (e.g., 'today 1-m', 'now 7-d')",
)
@click.option("--count", "-n", type=int, default=5, help="Number of opportunities to find")
@click.option("--export", "-e", is_flag=True, help="Export results to file")
@click.option("--export-path", type=str, help="Directory to save exported data")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "xlsx"]),
    default="csv",
    help="Export format",
)
@click.argument("seed_topics", nargs=-1)
def writing_opportunities(
    region: Optional[str],
    timeframe: str,
    count: int,
    export: bool,
    export_path: Optional[str],
    format: str,
    seed_topics,
):
    """Find specific writing opportunities based on trends."""
    try:
        client = TrendsClient()
        suggester = ContentSuggester(client)

        region_code = validate_region_code(region) if region else None
        timeframe_parsed = parse_timeframe(timeframe)

        seed_topics_list = list(seed_topics) if seed_topics else None

        with_spinner("Finding writing opportunities...")(lambda: None)()
        opportunities_df = suggester.get_writing_opportunities(
            seed_topics=seed_topics_list,
            region=region_code,
            timeframe=timeframe_parsed,
            count=count,
        )

        # Display results
        if opportunities_df.empty:
            console.print(
                "[yellow]No writing opportunities found for the given parameters.[/yellow]"
            )
            return

        region_display = region_code if region_code else client.get_current_region()
        region_name = format_region_name(region_display)

        # Create a rich table for display
        from rich.table import Table

        table = Table(title=f"Writing Opportunities - {region_name}")
        table.add_column("#", justify="right", style="dim")
        table.add_column("Opportunity", style="green")
        table.add_column("Related To", style="blue")
        table.add_column("Growth", justify="right")
        table.add_column("Suggestion", style="yellow")

        for i, (_, row) in enumerate(opportunities_df.iterrows(), 1):
            # Format growth value
            if row["growth_value"] >= 5000:
                growth_str = "Breakout"  # Google's term for >5000%
            else:
                growth_str = f"+{row['growth_value']:.0f}%"

            table.add_row(
                str(i), row["opportunity"], row["related_to"], growth_str, row["suggestion"]
            )

        console.print(table)

        # Export if requested
        if export:
            export_dir = validate_export_path(export_path)
            export_file = export_dir / f"writing_opportunities_{region_display}.{format}"
            export_to_file(opportunities_df, export_file, format)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@cli.command()
@click.argument("topics", nargs=-1, required=True)
@click.option(
    "--period",
    "-p",
    type=click.Choice(["4h", "24h", "48h", "7d"]),
    default="24h",
    help="Time period to analyze (4h, 24h, 48h, 7d)",
)
@click.option("--export", "-e", is_flag=True, help="Export results to file")
@click.option("--export-path", type=str, help="Directory to save exported data")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "xlsx"]),
    default="csv",
    help="Export format",
)
@click.option("--visualize", "-v", is_flag=True, help="Generate visualization")
def topic_growth(
    topics, period: str, export: bool, export_path: Optional[str], format: str, visualize: bool
):
    """Analyze growth patterns for multiple topics with independent normalization."""
    try:
        if not topics:
            console.print(
                "[bold red]Error:[/bold red] Please provide at least one topic to analyze."
            )
            return

        # Map period string to BatchPeriod enum
        period_map = {
            "4h": BatchPeriod.Past4H,
            "24h": BatchPeriod.Past24H,
            "48h": BatchPeriod.Past48H,
            "7d": BatchPeriod.Past7D,
        }

        batch_period = period_map[period]

        client = TrendsClient()
        suggester = ContentSuggester(client)

        # Max topics warning
        if len(topics) > 20:  # Show warning but don't truncate (TrendsPy can handle hundreds)
            console.print(
                "[bold yellow]Warning:[/bold yellow] Analyzing many topics. This may take a while."
            )

        with_spinner(f"Analyzing growth patterns for {len(topics)} topics...")(lambda: None)()
        growth_df = suggester.get_topic_growth_data(topics=list(topics), time_period=batch_period)

        # Display results
        if growth_df.empty:
            console.print("[yellow]No growth data found for the given topics.[/yellow]")
            return

        # Create visualization if requested
        viz_path = None
        if visualize and export:
            export_dir = validate_export_path(export_path)
            viz_path = export_dir / f"topic_growth_{period}.png"

        # Display formatted results
        format_interest_over_time(
            growth_df,
            title=f"Topic Growth Analysis - Past {period}",
            export_path=viz_path if visualize else None,
        )

        # Export if requested
        if export:
            export_dir = validate_export_path(export_path)
            export_file = export_dir / f"topic_growth_{period}.{format}"
            export_to_file(growth_df, export_file, format)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@cli.command()
@click.argument("query", type=str)
@click.option(
    "--region", "-r", help="Region code (e.g., US, GB, AE). Auto-detects if not specified."
)
@click.option(
    "--resolution",
    type=click.Choice(["COUNTRY", "REGION", "CITY", "DMA"]),
    default="COUNTRY",
    help="Geographic resolution level",
)
@click.option(
    "--timeframe", "-t", default="today 12-m", help="Timeframe for data (e.g., 'today 12-m')"
)
@click.option(
    "--category",
    type=str,
    default=DEFAULT_CATEGORY,
    help=f"Category ID to filter results. Default: {DEFAULT_CATEGORY} (All)",
)
@click.option("--count", "-n", type=int, default=20, help="Number of regions to display")
@click.option("--export", "-e", is_flag=True, help="Export results to file")
@click.option("--export-path", type=str, help="Directory to save exported data")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json", "xlsx"]),
    default="csv",
    help="Export format",
)
def geo_interest(
    query: str,
    region: Optional[str],
    resolution: str,
    timeframe: str,
    category: str,
    count: int,
    export: bool,
    export_path: Optional[str],
    format: str,
):
    """Show interest by geographic region for a query."""
    try:
        client = TrendsClient()

        region_code = validate_region_code(region) if region else None
        timeframe_parsed = parse_timeframe(timeframe)

        with_spinner(f"Fetching geographic interest data for '{query}'...")(lambda: None)()
        interest_df = client.get_interest_by_region(
            queries=query,
            region=region_code,
            timeframe=timeframe_parsed,
            category=category,
            resolution=resolution,
        )

        # Display results
        if interest_df.empty:
            console.print("[yellow]No geographic interest data found for the given query.[/yellow]")
            return

        region_display = region_code if region_code else client.get_current_region()
        region_name = format_region_name(region_display)

        # Format and display
        format_interest_by_region(
            interest_df,
            title=f"Geographic Interest for '{query}' - {region_name} ({resolution})",
            count=count,
        )

        # Export if requested
        if export:
            export_dir = validate_export_path(export_path)
            export_file = (
                export_dir / f"geo_interest_{query}_{region_display}_{resolution}.{format}"
            )
            export_to_file(interest_df, export_file, format)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@cli.command()
@click.option("--find", "-f", help="Search term to filter categories")
def categories(find: Optional[str]):
    """List available content categories."""
    try:
        client = TrendsClient()

        with_spinner("Fetching category information...")(lambda: None)()
        categories = client.get_categories(find=find)

        if not categories:
            if find:
                console.print(f"[yellow]No categories found matching '{find}'.[/yellow]")
            else:
                console.print("[yellow]No categories found.[/yellow]")
            return

        from rich.table import Table

        table = Table(title="Google Trends Categories")
        table.add_column("ID", style="dim")
        table.add_column("Category", style="green")

        for category in sorted(categories, key=lambda x: x["id"]):
            table.add_row(category["id"], category["name"])

        console.print(table)

        # Help text
        console.print("\n[dim]Use category IDs with the --category option in commands.[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@cli.command()
@click.argument("search_term", required=True)
def geo(search_term: str):
    """Search for location codes by name."""
    try:
        client = TrendsClient()

        with_spinner(f"Searching for locations matching '{search_term}'...")(lambda: None)()
        locations = client.get_geo_codes(find=search_term)

        if not locations:
            console.print(f"[yellow]No locations found matching '{search_term}'.[/yellow]")
            return

        from rich.table import Table

        table = Table(title=f"Locations Matching '{search_term}'")
        table.add_column("Code", style="dim")
        table.add_column("Location", style="green")

        for location in sorted(locations, key=lambda x: x["id"]):
            table.add_row(location["id"], location["name"])

        console.print(table)

        # Help text
        console.print("\n[dim]Use location codes with the --region option in commands.[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")


@cli.command()
def help_timeframe():
    """Show information on supported timeframe formats."""
    from rich.panel import Panel
    from rich.text import Text

    content = Text()

    content.append("Standard API timeframes:\n", style="bold")
    content.append("  'now 1-H', 'now 4-H', 'today 1-m', 'today 3-m', 'today 12-m'\n\n")

    content.append("Custom intervals:\n", style="bold")
    content.append("  Short-term (< 8 days): 'now 123-H', 'now 72-H'\n")
    content.append("  Long-term: 'today 45-d', 'today 90-d', 'today 18-m'\n\n")

    content.append("Date-based:\n", style="bold")
    content.append("  Start with date: '2024-02-01 10-d', '2024-03-15 3-m'\n")
    content.append("  Date ranges: '2024-01-01 2024-12-31'\n")
    content.append("  Hourly precision (for < 8 days): '2024-03-25T12 2024-03-25T15'\n\n")

    content.append("Special cases:\n", style="bold")
    content.append("  All available data: 'all'")

    panel = Panel(content, title="Supported Timeframe Formats", expand=False)
    console.print(panel)


def main():
    """Main entry point for the Google Trends CLI."""
    try:
        cli()
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
