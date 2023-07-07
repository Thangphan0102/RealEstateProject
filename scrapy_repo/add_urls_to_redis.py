from redis import from_url
from scrapy_repo.settings import REDIS_URL
import json
import argparse

def main(args):
    # Create a redis client
    redis_client = from_url(REDIS_URL)
    
    for i in range(args.first, args.last+1):
        redis_client.lpush(
            "mogi_vn_queue:start_urls",
            json.dumps(
                {
                    "url": f"https://mogi.vn/{args.type}?cp={i}"
                }
            )
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Add urls redis for crawling")
    parser.add_argument("type", type=str, help="property type want to crawl")
    parser.add_argument("first", type=int, help="first page want to crawl")
    parser.add_argument("last", type=int, help="last page want to crawl")
    args = parser.parse_args()
    main(args)
