from aiogram import Router
from create_bot import dp, bot
from utils.check_nfts import check_sold_nfts, check_new_nfts
import asyncio
import logging
import sys


async def main():
    await asyncio.gather(dp.start_polling(bot), check_sold_nfts(), check_new_nfts())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
