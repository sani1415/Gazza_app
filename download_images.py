#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download and cache article images locally."""

import argparse
import json
import os
from pathlib import Path
from urllib.parse import urlparse, unquote

import requests

DEFAULT_OUTPUT_DIR = Path("images_cache")
ARTICLES_FILE = Path("articles_combined.json")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Download article images for offline use.")
    parser.add_argument(
        "--date",
        help="Specify a YYYY-MM-DD date to download images for a single day. If omitted, downloads for all dates.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to store downloaded images (default: images_cache)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of images to download (useful for testing).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Redownload images even if the file already exists.",
    )
    return parser.parse_args()


def load_articles():
    if not ARTICLES_FILE.exists():
        raise FileNotFoundError(f"Cannot find {ARTICLES_FILE}. Make sure you run the script from the project root.")

    with ARTICLES_FILE.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def filter_articles(articles, target_date=None):
    filtered = [article for article in articles if article.get("image_url")]
    if target_date:
        filtered = [article for article in filtered if article.get("date") == target_date]
    return filtered


def build_filename(article, output_dir: Path):
    image_url = article["image_url"]
    parsed = urlparse(image_url)
    # Extract filename and extension from URL path
    basename = Path(unquote(parsed.path)).name
    if not basename:
        basename = f"article_{article.get('id', 'unknown')}"

    stem, ext = os.path.splitext(basename)
    if not ext:
        ext = ".jpg"

    article_date = article.get("date") or "unknown_date"
    safe_date = article_date.replace("/", "-")
    target_dir = output_dir / safe_date
    target_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{article.get('id', 'article')}_{stem}{ext}"
    return target_dir / filename


def download_image(url: str, destination: Path, force: bool = False):
    if destination.exists() and not force:
        return False  # skipped

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    destination.write_bytes(response.content)
    return True


def main():
    args = parse_arguments()

    all_articles = load_articles()
    articles = filter_articles(all_articles, args.date)

    if not articles:
        message = "لم يتم العثور على مقالات تحتوي على صور"
        if args.date:
            message += f" في التاريخ {args.date}"
        print(message)
        return

    print("📷 بدء تحميل الصور...")
    if args.date:
        print(f"📅 التاريخ: {args.date}")
    print(f"📁 مجلد التخزين: {args.output.resolve()}")
    if args.limit:
        print(f"🔢 الحد الأقصى للصور: {args.limit}")
    if args.force:
        print("⚠️ سيتم إعادة تحميل الصور حتى لو كانت موجودة مسبقًا")

    downloaded = 0
    skipped = 0
    errors = 0

    for article in articles:
        if args.limit and downloaded >= args.limit:
            break

        destination = build_filename(article, args.output)
        image_url = article["image_url"]

        try:
            changed = download_image(image_url, destination, args.force)
            if changed:
                downloaded += 1
                print(f"✅ تم التحميل: {destination.relative_to(args.output)}")
            else:
                skipped += 1
        except requests.RequestException as exc:
            errors += 1
            print(f"❌ خطأ في تحميل الصورة ({image_url}): {exc}")

    print("\n🚩 ملخص التحميل:")
    print(f"   الصور الجديدة: {downloaded}")
    print(f"   الصور المتخطاة (موجودة مسبقًا): {skipped}")
    print(f"   أخطاء التحميل: {errors}")


if __name__ == "__main__":
    main()
