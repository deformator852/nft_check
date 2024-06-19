from create_bot import bot  # pyright:ignore
import aiohttp
import asyncio
import datetime

url = "https://api.opensea.io/api/v2/events/collection/museum-of-fofar"
headers = {
    "Accept": "application/json",
    "x-api-key": "",
}
group_id = -000

async def check_sold_nfts():
    while True:
        now = datetime.datetime.now(datetime.UTC)
        one_minute_ago = now - datetime.timedelta(seconds=15)
        params = {
            "event_type": "sale",
            "before": int(now.timestamp()),
            "after": int(one_minute_ago.timestamp()),
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers, params=params) as response:
                data = await response.json()
                asset_events = data.get("asset_events")
                if len(asset_events) > 0:
                    eth_to_usd_rate = await eth_to_usd()
                    for event in asset_events:
                        nft = event.get("nft")
                        answer = await build_sold_answer(
                            nft, event.get("payment"), eth_to_usd_rate
                        )
                        await bot.send_message(group_id, answer)
        await asyncio.sleep(15)


async def check_new_nfts():
    while True:
        now = datetime.datetime.now(datetime.UTC)
        one_minute_ago = now - datetime.timedelta(minutes=1)
        params = {
            "event_type": "listing",
            "before": int(now.timestamp()),
            "after": int(one_minute_ago.timestamp()),
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url=url, headers=headers, params=params) as response:
                data = await response.json()
                asset_events = data.get("asset_events")
                if len(asset_events) > 0:
                    eth_to_usd_rate = await eth_to_usd()
                    for event in asset_events:
                        answer = await build_new_answer(
                            event.get("asset"), event.get("payment"), eth_to_usd_rate
                        )
                        await bot.send_message(group_id, answer)

        await asyncio.sleep(60)


async def build_new_answer(asset, payment, eth_to_usd_rate):
    title = asset.get("name")
    payment_quantity = payment["quantity"]
    decimals = payment["decimals"]
    price = int(payment_quantity) / (10**decimals)
    price_usd = int(price * eth_to_usd_rate)
    opensea_url = asset["opensea_url"]
    answer = f"""
🖼️ New Listing in Museum of Fofar!
🎨 {title} was just listed for {price} ETH (${price_usd})
🔗 View it here: {opensea_url}
    """
    return answer


async def build_sold_answer(nft, payment, eth_to_usd_rate):
    title = nft["name"]
    payment_quantity = payment["quantity"]
    decimals = payment["decimals"]
    price = int(payment_quantity) / (10**decimals)
    price_usd = int(price * eth_to_usd_rate)
    opensea_url = nft["opensea_url"]
    answer = f"""
🎉 Meme Sold in Museum of Fofar!
🎨{title} was sold for {price} ETH (${price_usd})
🪙 5% Donated to Fofar Marketing Wallet
🔗 View it here:{opensea_url}
"""
    return answer


async def eth_to_usd():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "ethereum", "vs_currencies": "usd"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            status = response.status
            if status == 200:
                data = await response.json()
                return data["ethereum"]["usd"]
            else:
                return 1
