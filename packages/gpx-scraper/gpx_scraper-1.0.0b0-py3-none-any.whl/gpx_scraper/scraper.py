#!/usr/bin/env python3
"""
GPX Scraper - A tool for downloading GPX files from websites.
"""

import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin
import time
import random
import argparse
import sys


def clean_title(title):
    """
    Cleans up a page title by removing common words and formatting it for use as a folder name.
    
    Args:
        title (str): The original page title
    
    Returns:
        str: The cleaned title suitable for a folder name
    """
    # Remove common phrases
    title = re.sub(r'Hiking Around\s+', '', title)
    title = re.sub(r'\s+Overview$', '', title)
    
    # Replace special characters with spaces
    title = re.sub(r'[\/:*?"<>|]', ' ', title)
    
    # Replace multiple spaces with a single space
    title = re.sub(r'\s+', ' ', title)
    
    # Trim whitespace
    title = title.strip()
    
    return title


def split_title_into_parts(title):
    """
    Splits a title into parts for hierarchical folder structure.
    
    Args:
        title (str): The cleaned page title
    
    Returns:
        list: Parts of the title for folder hierarchy
    """
    # Try to split by common separators
    for separator in [",", " - ", " – ", " | ", " > "]:
        if separator in title:
            parts = [part.strip() for part in title.split(separator)]
            return [part for part in parts if part]  # Filter out empty parts
    
    # If no separators found, return the whole title as a single part
    return [title]


def download_gpx_zip(url, download_dir='downloads'):
    """
    Downloads a .gpx.zip file from the given URL.
    
    Args:
        url (str): The URL of the webpage containing the .gpx.zip file link
        download_dir (str): Base directory for downloads
    
    Returns:
        str: The path to the downloaded file, or None if no file was found
    """
    try:
        # Get the webpage content
        response = requests.get(url)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract page title
        page_title = soup.title.text.strip() if soup.title else "Unknown"
        cleaned_title = clean_title(page_title)
        print(f"Page title: {page_title}")
        print(f"Using folder name: {cleaned_title}")
        
        # Find all links that end with .gpx.zip
        gpx_links = [a['href'] for a in soup.find_all('a', href=True)
                    if a['href'].strip().lower().endswith('.gpx.zip')]
        
        if not gpx_links:
            print(f"No .gpx.zip files found on the page: {url}")
            return None
            
        # Get the first .gpx.zip link
        gpx_url = urljoin(url, gpx_links[0])
        print(f"Found .gpx.zip file: {gpx_url}")
        
        # Download the file
        file_response = requests.get(gpx_url)
        file_response.raise_for_status()
        
        # Create downloads directory if it doesn't exist
        os.makedirs(download_dir, exist_ok=True)
        
        # Create subdirectory based on page title
        page_title = soup.title.text.strip() if soup.title else "Unknown"
        cleaned_title = clean_title(page_title)
        
        # Split title into parts for hierarchical folder structure
        title_parts = split_title_into_parts(cleaned_title)
        
        # Create hierarchical folder structure
        folder_path = download_dir
        for part in title_parts:
            folder_path = os.path.join(folder_path, part)
            os.makedirs(folder_path, exist_ok=True)
            
        print(f"Created folder structure: {folder_path}")
        
        # Save the file in the appropriate subdirectory
        filename = os.path.basename(gpx_url)
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'wb') as f:
            f.write(file_response.content)
        
        print(f"Successfully downloaded {filename}")
        return file_path
        
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def parse_link_list(list_url, create_subfolders=True, download_dir='downloads'):
    """
    Parses a webpage containing a list of links and processes each link.
    
    Args:
        list_url (str): The URL of the webpage containing the list of links
        create_subfolders (bool): Whether to create hierarchical subfolders
        download_dir (str): Base directory for downloads
    
    Returns:
        list: A list of downloaded file paths
    """
    try:
        # Get the webpage content
        response = requests.get(list_url)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract main page title for potential parent folder
        main_page_title = soup.title.text.strip() if soup.title else "Unknown"
        cleaned_main_title = clean_title(main_page_title)
        
        # Split main title into parts for hierarchical folder structure
        main_title_parts = split_title_into_parts(cleaned_main_title)
        print(f"Main page title: {main_page_title}")
        print(f"Using folder hierarchy: {' > '.join(main_title_parts)}")
        
        # Find all links in the page
        links = [a['href'] for a in soup.find_all('a', href=True)]
        
        if not links:
            print("No links found on the page.")
            return []
        
        print(f"Found {len(links)} links on the page.")
        
        # Process each link
        downloaded_files = []
        for i, link in enumerate(links):
            full_url = urljoin(list_url, link)
            print(f"\nProcessing link {i+1}/{len(links)}: {full_url}")
            
            # Download GPX file if available
            file_path = download_gpx_zip(full_url, download_dir)
            if file_path:
                downloaded_files.append(file_path)
            
            # Add a small delay to avoid overwhelming the server
            if i < len(links) - 1:  # No need to sleep after the last request
                sleep_time = random.uniform(1, 3)
                print(f"Waiting {sleep_time:.2f} seconds before next request...")
                time.sleep(sleep_time)
        
        return downloaded_files
        
    except requests.exceptions.RequestException as e:
        print(f"Error during request: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def main():
    """Main entry point for the GPX scraper command-line tool."""
    parser = argparse.ArgumentParser(description='GPX Scraper - Download GPX files from websites')
    parser.add_argument('--version', action='version', 
                        version=f'%(prog)s {__import__("gpx_scraper").__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Single download command
    single_parser = subparsers.add_parser('download', help='Download a single GPX file')
    single_parser.add_argument('url', help='URL of the page containing the GPX file')
    single_parser.add_argument('--output-dir', '-o', default='downloads',
                              help='Directory to save downloaded files (default: downloads)')
    
    # Batch download command
    batch_parser = subparsers.add_parser('batch', help='Download multiple GPX files from a list')
    batch_parser.add_argument('url', help='URL of the page containing links to GPX files')
    batch_parser.add_argument('--organize', '-g', action='store_true',
                             help='Organize downloads into subfolders based on page titles')
    batch_parser.add_argument('--output-dir', '-o', default='downloads',
                             help='Directory to save downloaded files (default: downloads)')
    
    # Interactive mode command
    interactive_parser = subparsers.add_parser('interactive', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'download':
        download_gpx_zip(args.url, args.output_dir)
    
    elif args.command == 'batch':
        downloaded_files = parse_link_list(args.url, args.organize, args.output_dir)
        
        if downloaded_files:
            print(f"\nSummary: Downloaded {len(downloaded_files)} files:")
            for file_path in downloaded_files:
                print(f"- {file_path}")
        else:
            print("\nNo files were downloaded.")
    
    elif args.command == 'interactive':
        print("GPX Scraper")
        print("===========")
        print("1. Download a single .gpx.zip file")
        print("2. Parse a list of links and download all .gpx.zip files")
        
        choice = input("\nEnter your choice (1 or 2): ")
        
        if choice == "1":
            url = input("Enter the URL to scrape: ")
            download_dir = input("Enter download directory (default: downloads): ") or "downloads"
            download_gpx_zip(url, download_dir)
        elif choice == "2":
            list_url = input("Enter the URL containing the list of links: ")
            create_subfolders = input("Create organized subfolders based on page titles? (y/n): ").lower() == 'y'
            download_dir = input("Enter download directory (default: downloads): ") or "downloads"
            downloaded_files = parse_link_list(list_url, create_subfolders, download_dir)
            
            if downloaded_files:
                print(f"\nSummary: Downloaded {len(downloaded_files)} files:")
                for file_path in downloaded_files:
                    print(f"- {file_path}")
            else:
                print("\nNo files were downloaded.")
        else:
            print("Invalid choice. Please run the script again and select 1 or 2.")


if __name__ == "__main__":
    main()
