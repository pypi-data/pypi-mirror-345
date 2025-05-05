from argparse import ArgumentParser
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

import traceback

from mdfb.core.get_post_identifiers import get_post_identifiers
from mdfb.core.fetch_post_details import fetch_post_details
from mdfb.core.download_blobs import download_blobs
from mdfb.core.resolve_handle import resolve_handle
from mdfb.utils.validation import *
from mdfb.utils.helpers import split_list
from mdfb.utils.database import connect_db, delete_user, check_user_has_posts
from mdfb.utils.logging import setup_logging
from mdfb.utils.constants import DEFAULT_THREADS 

def fetch_posts(did: str, post_types: dict, limit: int = 0, archive: bool = False, update: bool = False) -> list[str]:
    post_uris = []
    for post_type, wanted in post_types.items():
        if wanted:
            if update:
                if check_user_has_posts(connect_db().cursor(), did, post_type):
                    post_uris.extend(get_post_identifiers(did, post_type, limit=limit, archive=archive, update=update))
                else:
                    raise ValueError(f"This user has no post in database for feed_type: {post_type}, cannot update as you have not downloaded any post for feed_type: {post_type}.")
            else:
                post_uris.extend(get_post_identifiers(did, post_type, limit=limit, archive=archive, update=update))
    return post_uris

def process_posts(posts: list, num_threads: int) -> list[dict]:
    """
    process_posts: processes the given list of post URIs to get the post details required for downloading, can be threaded 

    Args:
        posts (list): list of URIs of the post wanted
        num_threads (int): number of threads 

    Returns:
        list[dict]: list of dictionaries that contain post details for each post
    """
    posts = split_list(posts, num_threads)
    post_details = []
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for post_batch in posts:
            futures.append(executor.submit(fetch_post_details, post_batch))
        for future in as_completed(futures):
            post_details.extend(future.result())
    return post_details

def main():
    parser = ArgumentParser()

    subparsers = parser.add_subparsers(dest="subcommand", required=False)

    database_parser = subparsers.add_parser("db", help="Manage the database")
    database_parser.add_argument("--delete_user", action="store", help="Delete all posts from this user")

    download_parser = subparsers.add_parser("download", help="Download posts")
    download_parser.add_argument("directory", action="store", help="Directory for where all downloaded post will be stored")
    download_parser.add_argument("--like", action="store_true", help="To retreive liked posts")
    download_parser.add_argument("--post", action="store_true", help="To retreive posts")
    download_parser.add_argument("--repost", action="store_true", help="To retreive reposts")
    download_parser.add_argument("--threads", action="store", help=f"Number of threads, maximum of {MAX_THREADS} threads")
    download_parser.add_argument("--format", action="store", help="Format string for filename e.g '{RKEY}_{DID}'. Valid keywords are: [RKEY, HANDLE, TEXT, DISPLAY_NAME, DID]")

    group_archive_limit = download_parser.add_mutually_exclusive_group(required=True)
    group_archive_limit.add_argument("--limit", "-l", action="store", help="The number of posts to be downloaded") 
    group_archive_limit.add_argument("--archive", action="store_true", help="To archive all posts of the specified types")
    group_archive_limit.add_argument("--update", "-u", action="store_true", help="Downloads latest posts that haven't been downloaded")

    group_identifier = download_parser.add_mutually_exclusive_group(required=True)
    group_identifier.add_argument("--did", "-d", action="store", help="The DID associated with the account")
    group_identifier.add_argument("--handle", action="store", help="The handle for the account e.g. johnny.bsky.social")
    
    args = parser.parse_args()
    try:
        if getattr(args, "delete_user", False):
            did = resolve_handle(args.delete_user)
            delete_user(did)
            return 

        did = validate_did(args.did) if args.did else resolve_handle(args.handle)
        directory = validate_directory(args.directory)
        filename_format_string = validate_format(args.format) if args.format else ""
        validate_database()
        setup_logging(directory)

        num_threads = validate_threads(args.threads) if args.threads else DEFAULT_THREADS
        
        if not any([args.like, args.post, args.repost]):
            raise ValueError("At least one flag (--like, --post, --repost) must be set.")
        
        post_types = {
            "like": args.like,
            "repost": args.repost,
            "post": args.post
        }

        print("Fetching post identifiers...")
        if args.archive:
            posts = fetch_posts(did, post_types, archive=True)
        elif args.update:
            posts = fetch_posts(did, post_types, archive=True, update=True)
        else:
            limit = validate_limit(args.limit)
            posts = fetch_posts(did, post_types, limit=limit)

        wanted_post_types = [post_type for post_type, wanted in post_types.items() if wanted]
        account = args.handle if args.handle else did
        validate_no_posts(posts, account, wanted_post_types, args.update)

        print("Getting post details...")
        post_details = process_posts(posts, num_threads)

        num_of_posts = len(post_details)
        post_links = split_list(post_details, num_threads)

        with tqdm(total=num_of_posts, desc="Downloading files") as progress_bar:
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                for batch_post_link in post_links:
                    if not filename_format_string:
                        futures.append(executor.submit(download_blobs, batch_post_link, directory, progress_bar))
                    else:
                        futures.append(executor.submit(download_blobs, batch_post_link, directory, progress_bar, filename_format_string))
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    main()  