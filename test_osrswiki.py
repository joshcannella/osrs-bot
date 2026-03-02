#!/usr/bin/env python3
import asyncio
import httpx

WIKI_API = "https://oldschool.runescape.wiki/api.php"
PRICES_API = "https://prices.runescape.wiki/api/v1/osrs"
USER_AGENT = "ChromaScape-MCP/1.0"

async def test_all():
    async with httpx.AsyncClient() as client:
        print("1. Testing bucket query (Iron ore)...")
        r = await client.get(WIKI_API, params={
            "action": "bucket",
            "query": "bucket('infobox_item').select('item_id','examine').where('item_name','Iron ore').run()",
            "format": "json"
        }, headers={"User-Agent": USER_AGENT})
        print(f"   Status: {r.status_code}, Data: {r.json()}\n")
        
        print("2. Testing wiki search (Dragon scimitar)...")
        r = await client.get(WIKI_API, params={
            "action": "opensearch",
            "search": "Dragon scimitar",
            "limit": 3,
            "format": "json"
        }, headers={"User-Agent": USER_AGENT})
        print(f"   Status: {r.status_code}, Results: {r.json()[1]}\n")
        
        print("3. Testing item prices (Iron ore, ID 440)...")
        r = await client.get(f"{PRICES_API}/latest", params={"id": 440}, headers={"User-Agent": USER_AGENT})
        print(f"   Status: {r.status_code}, Data: {r.json()}\n")
        
        print("4. Testing item mapping (first 3 items)...")
        r = await client.get(f"{PRICES_API}/mapping", headers={"User-Agent": USER_AGENT})
        data = r.json()
        print(f"   Status: {r.status_code}, Total items: {len(data)}")
        print(f"   Sample: {data[:3]}\n")

asyncio.run(test_all())
