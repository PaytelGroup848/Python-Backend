import asyncio


async def worker():

    while True:

        await asyncio.sleep(5)


if __name__ == "__main__":

    asyncio.run(
        worker()
    )