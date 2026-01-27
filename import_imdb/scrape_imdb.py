#!/usr/bin/env python3
# /// script
# dependencies = [
#   "beautifulsoup4>=4.12.0",
#   "httpx>=0.27.0",
# ]
# ///
"""
IMDB HTML Scraper

Downloads and parses IMDB movie pages to extract relevant information.

Usage:
    uv run scrape_imdb.py https://www.imdb.com/title/tt32536315
    uv run scrape_imdb.py tt32536315
    uv run scrape_imdb.py --file links.txt
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

import httpx
from bs4 import BeautifulSoup


class IMDBScraper:
    """Scraper for IMDB movie pages."""

    BASE_URL = "https://www.imdb.com"
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self, imdb_id_or_url):
        """
        Initialize the scraper with an IMDB ID or URL.

        Args:
            imdb_id_or_url: Either a full URL or just the IMDB ID (e.g., 'tt32536315')
        """
        self.imdb_id = self._extract_imdb_id(imdb_id_or_url)
        self.url = f"{self.BASE_URL}/title/{self.imdb_id}/"
        self.html = None
        self.soup = None

    def _extract_imdb_id(self, imdb_id_or_url):
        """Extract IMDB ID from URL or validate ID format."""
        if imdb_id_or_url.startswith("http"):
            # Extract ID from URL
            match = re.search(r"/title/(tt\d+)", imdb_id_or_url)
            if match:
                return match.group(1)
            raise ValueError(f"Could not extract IMDB ID from URL: {imdb_id_or_url}")
        elif imdb_id_or_url.startswith("tt"):
            return imdb_id_or_url
        else:
            # Assume it's just the numeric part
            return f"tt{imdb_id_or_url}"

    def download(self):
        """Download the HTML page."""
        print(f"Downloading: {self.url}")
        try:
            response = httpx.get(self.url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()
            self.html = response.text
            self.soup = BeautifulSoup(self.html, "html.parser")
            print(f"Downloaded {len(self.html)} bytes")
            return True
        except httpx.HTTPError as e:
            print(f"Error downloading page: {e}", file=sys.stderr)
            return False

    def parse(self):
        """
        Parse the downloaded HTML and extract movie information.

        Returns:
            dict: Dictionary containing extracted movie information
        """
        if not self.soup:
            raise ValueError("No HTML loaded. Call download() first.")

        data = {
            "imdb_id": self.imdb_id,
            "url": self.url,
            "title": self._get_title(),
            "year": self._get_year(),
            "rating": self._get_rating(),
            "genres": self._get_genres(),
            "director": self._get_director(),
            "cast": self._get_cast(),
            "plot": self._get_plot(),
            "runtime": self._get_runtime(),
            "poster_url": self._get_poster_url(),
        }

        return data

    def _get_title(self):
        """Extract movie title."""
        # Try multiple selectors as IMDB changes their HTML structure
        title_element = self.soup.find("h1", {"data-testid": "hero__pageTitle"})
        if title_element:
            return title_element.get_text(strip=True)

        # Fallback to meta tags
        og_title = self.soup.find("meta", property="og:title")
        if og_title:
            title = og_title.get("content", "")
            # Remove year from title if present
            title = re.sub(r"\s*\(\d{4}\)\s*$", "", title)
            return title

        return None

    def _get_year(self):
        """Extract release year."""
        # Try to find year in the title section
        year_element = self.soup.find("a", href=re.compile(r"/title/tt\d+/releaseinfo"))
        if year_element:
            year_text = year_element.get_text(strip=True)
            match = re.search(r"\d{4}", year_text)
            if match:
                return int(match.group())

        # Try the hero section
        hero_section = self.soup.find("section", {"data-testid": "Hero"})
        if hero_section:
            year_links = hero_section.find_all("a", href=re.compile(r"/releaseinfo"))
            for link in year_links:
                match = re.search(r"\d{4}", link.get_text())
                if match:
                    return int(match.group())

        return None

    def _get_rating(self):
        """Extract IMDB rating."""
        rating_element = self.soup.find("span", {"class": re.compile(r"sc-.*-rating")})
        if rating_element:
            rating_text = rating_element.get_text(strip=True)
            match = re.search(r"([\d.]+)", rating_text)
            if match:
                return float(match.group(1))

        # Try data-testid approach
        rating_element = self.soup.find(
            "div", {"data-testid": "hero-rating-bar__aggregate-rating__score"}
        )
        if rating_element:
            span = rating_element.find("span")
            if span:
                match = re.search(r"([\d.]+)", span.get_text(strip=True))
                if match:
                    return float(match.group(1))

        return None

    def _get_genres(self):
        """Extract genres."""
        genres = []

        # Try chip elements
        genre_elements = self.soup.find_all(
            "a", {"class": re.compile(r".*GenresAndPlot.*")}
        )
        for element in genre_elements:
            if "/search/title" in element.get("href", ""):
                genres.append(element.get_text(strip=True))

        # Try span elements with genre data
        if not genres:
            genre_section = self.soup.find("div", {"data-testid": "genres"})
            if genre_section:
                for link in genre_section.find_all("a"):
                    genres.append(link.get_text(strip=True))

        return genres if genres else None

    def _get_director(self):
        """Extract director name."""
        # Look for director in credits
        director_section = self.soup.find(
            "li", {"data-testid": "title-pc-principal-credit"}
        )
        if director_section:
            director_link = director_section.find("a", href=re.compile(r"/name/nm\d+"))
            if director_link:
                return director_link.get_text(strip=True)

        return None

    def _get_cast(self, limit=5):
        """Extract top cast members."""
        cast = []

        # Find cast section
        cast_section = self.soup.find("section", {"data-testid": "title-cast"})
        if cast_section:
            cast_links = cast_section.find_all(
                "a", href=re.compile(r"/name/nm\d+"), limit=limit * 2
            )
            for link in cast_links:
                name = link.get_text(strip=True)
                if name and name not in cast:
                    cast.append(name)
                if len(cast) >= limit:
                    break

        return cast if cast else None

    def _get_plot(self):
        """Extract plot summary."""
        # Try multiple approaches
        plot_element = self.soup.find("span", {"data-testid": "plot-xl"})
        if plot_element:
            return plot_element.get_text(strip=True)

        plot_element = self.soup.find("span", {"data-testid": "plot-l"})
        if plot_element:
            return plot_element.get_text(strip=True)

        # Fallback to meta description
        meta_desc = self.soup.find("meta", {"name": "description"})
        if meta_desc:
            return meta_desc.get("content", "").strip()

        return None

    def _get_runtime(self):
        """Extract runtime in minutes."""
        runtime_element = self.soup.find(
            "li", {"data-testid": "title-techspec_runtime"}
        )
        if runtime_element:
            runtime_text = runtime_element.get_text(strip=True)
            match = re.search(r"(\d+)\s*(?:min|minute)", runtime_text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def _get_poster_url(self):
        """Extract poster image URL."""
        # Try hero image
        img_element = self.soup.find("img", {"class": re.compile(r".*Poster.*")})
        if img_element:
            return img_element.get("src")

        # Try meta tag
        og_image = self.soup.find("meta", property="og:image")
        if og_image:
            return og_image.get("content")

        return None

    def save_html(self, filename=None):
        """Save the raw HTML to a file."""
        if not self.html:
            raise ValueError("No HTML loaded. Call download() first.")

        if filename is None:
            filename = f"{self.imdb_id}.html"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(self.html)
        print(f"Saved HTML to: {filename}")

    def save_json(self, data, filename=None):
        """Save parsed data as JSON."""
        if filename is None:
            filename = f"{self.imdb_id}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved JSON to: {filename}")

    def download_poster(self, poster_url, output_path):
        """
        Download poster image to local file.

        Args:
            poster_url: URL of the poster image
            output_path: Path to save the image

        Returns:
            bool: True if successful, False otherwise
        """
        if not poster_url:
            print("No poster URL available")
            return False

        try:
            print(f"Downloading poster from: {poster_url}")
            response = httpx.get(poster_url, headers=self.HEADERS, timeout=10)
            response.raise_for_status()

            # Determine file extension from URL or content type
            ext = self._get_image_extension(
                poster_url, response.headers.get("content-type")
            )
            output_path = Path(output_path)

            # Add extension if not present
            if not output_path.suffix:
                output_path = output_path.with_suffix(ext)

            with open(output_path, "wb") as f:
                f.write(response.content)

            print(f"Saved poster to: {output_path}")
            return True

        except httpx.HTTPError as e:
            print(f"Error downloading poster: {e}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"Error saving poster: {e}", file=sys.stderr)
            return False

    def _get_image_extension(self, url, content_type=None):
        """Determine image file extension from URL or content type."""
        # Try to get extension from URL
        if "." in url:
            ext = Path(url).suffix.split("?")[0]  # Remove query params
            if ext.lower() in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                return ext

        # Fallback to content type
        if content_type:
            content_type_map = {
                "image/jpeg": ".jpg",
                "image/png": ".png",
                "image/gif": ".gif",
                "image/webp": ".webp",
            }
            return content_type_map.get(content_type.split(";")[0].strip(), ".jpg")

        # Default to jpg
        return ".jpg"


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Download and parse IMDB movie pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run scrape_imdb.py https://www.imdb.com/title/tt32536315
  uv run scrape_imdb.py tt32536315
  uv run scrape_imdb.py --file links.txt --save-json
  uv run scrape_imdb.py --file links.txt --output-dir data
        """,
    )
    parser.add_argument(
        "imdb_id_or_url",
        nargs="?",
        help="IMDB ID (e.g., tt32536315) or full URL",
    )
    parser.add_argument(
        "--file",
        "-f",
        type=str,
        help="File containing list of IMDB URLs or IDs (one per line)",
    )
    parser.add_argument(
        "--save-html",
        action="store_true",
        help="Save raw HTML to file",
    )
    parser.add_argument(
        "--save-json",
        action="store_true",
        help="Save parsed data as JSON",
    )
    parser.add_argument(
        "--save-posters",
        action="store_true",
        help="Download and save poster images",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory to save output files (default: current directory)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between requests in seconds (default: 1.0)",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.imdb_id_or_url and not args.file:
        parser.error("Either provide an IMDB ID/URL or use --file option")

    if args.imdb_id_or_url and args.file:
        parser.error("Cannot use both IMDB ID/URL and --file option")

    # Setup output directory
    output_dir = Path(args.output_dir) if args.output_dir else Path.cwd()
    if args.output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Setup images directory
    images_dir = output_dir / "out_images"
    if args.save_posters:
        images_dir.mkdir(parents=True, exist_ok=True)

    # Get list of IDs to process
    if args.file:
        imdb_ids = load_ids_from_file(args.file)
        if not imdb_ids:
            print("No valid IMDB IDs found in file", file=sys.stderr)
            sys.exit(1)
        print(f"Found {len(imdb_ids)} IMDB IDs to process")
    else:
        imdb_ids = [args.imdb_id_or_url]

    # Process each ID
    results = []
    failed = []

    for i, imdb_id_or_url in enumerate(imdb_ids, 1):
        print(f"\n[{i}/{len(imdb_ids)}] Processing: {imdb_id_or_url}")
        print("-" * 60)

        try:
            scraper = IMDBScraper(imdb_id_or_url)

            if not scraper.download():
                failed.append(imdb_id_or_url)
                continue

            data = scraper.parse()
            results.append(data)

            # Print results for this movie
            print(f"Title: {data.get('title')}")
            print(f"Year: {data.get('year')}")
            print(f"Rating: {data.get('rating')}")
            print(f"Director: {data.get('director')}")

            # Save files if requested
            if args.save_html:
                if args.output_dir:
                    html_path = output_dir / f"{scraper.imdb_id}.html"
                    scraper.save_html(str(html_path))
                else:
                    scraper.save_html()

            if args.save_json:
                if args.output_dir:
                    json_path = output_dir / f"{scraper.imdb_id}.json"
                    scraper.save_json(data, str(json_path))
                else:
                    scraper.save_json(data)

            if args.save_posters and data.get("poster_url"):
                poster_path = images_dir / scraper.imdb_id
                scraper.download_poster(data["poster_url"], poster_path)

            # Delay between requests (except for last one)
            if i < len(imdb_ids):
                time.sleep(args.delay)

        except Exception as e:
            print(f"Error processing {imdb_id_or_url}: {e}", file=sys.stderr)
            failed.append(imdb_id_or_url)
            import traceback

            traceback.print_exc()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total processed: {len(imdb_ids)}")
    print(f"Successful: {len(results)}")
    print(f"Failed: {len(failed)}")

    if failed:
        print("\nFailed IDs:")
        for failed_id in failed:
            print(f"  - {failed_id}")

    # Save combined results if processing multiple
    if len(results) > 1 and args.save_json:
        combined_path = output_dir / "all_movies.json"
        with open(combined_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nSaved combined results to: {combined_path}")

    sys.exit(0 if not failed else 1)


def load_ids_from_file(filepath):
    """
    Load IMDB IDs or URLs from a file.

    Args:
        filepath: Path to file containing IMDB IDs/URLs (one per line)

    Returns:
        list: List of cleaned IMDB IDs/URLs
    """
    ids = []
    path = Path(filepath)

    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        return ids

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith("#"):
                ids.append(line)

    return ids


if __name__ == "__main__":
    main()
