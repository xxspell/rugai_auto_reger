import asyncio
from itertools import cycle
from os.path import exists

from better_proxy import Proxy

from core import start_reger
from utils import logger, loader


async def main(proxies_list, proxies_cycled, software_method, threads):
    semaphore = asyncio.Semaphore(value=threads)

    async def run_task(proxy):
        async with semaphore:
            await start_reger(software_method=software_method, proxy=proxy)

    tasks = [run_task(proxy) for proxy in proxies_list]

    await asyncio.gather(*tasks)


def run():
    if exists(path='proxies.txt'):
        proxies_list: list[str] = [proxy.as_url for proxy in Proxy.from_file(filepath='proxies.txt')]

    else:
        proxies_list: list[str] = []
    if exists(path='accounts.txt'):
        with open(file='accounts.txt',
                  mode='r',
                  encoding='utf-8-sig') as file:
            accounts_list: list[str] = [row.strip() if row.strip().startswith('0x')
                                        else f'0x{row.strip()}' for row in file]

    else:
        accounts_list: list[str] = []

    proxies_cycled: cycle | None = cycle(proxies_list) if proxies_list else None
    logger.success(f'Successfully loaded {len(proxies_list)} proxies')

    threads: int = int(input('\nThreads: '))
    software_method: int = int(input('\n1. Register 1 account per 1 proxy\n'
                                     'Choose: '))
    print()
    try:
        asyncio.run(main(proxies_list, proxies_cycled, software_method, threads))
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    logger.success('Work Has Been Successfully Finished')
    input('\nPress Enter to Exit..')

if __name__ == '__main__':
    from sys import platform

    if platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    run()