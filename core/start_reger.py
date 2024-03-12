import json
import re
import time
import traceback
from itertools import cycle
from random import choice

from fake_useragent import UserAgent

import aiofiles
import aiohttp
from bs4 import BeautifulSoup
from utils.pyemailnator import CreateClient
from utils import logger, get_connector, ref_codes, generate_password


class Reger:
    def __init__(self):
        self.ref_code: str = ''
        # logger.debug("Init reger")

    async def register(self, data, client: aiohttp.ClientSession) -> str:
        r = await client.post(url='https://api.rug.ai/v1/auth/email/create',
                              data=json.dumps(data),
                              verify_ssl=False)
        # logger.debug(f"POST https://api.rug.ai/v1/auth/email/create {data} / {await r.json()}")

        return await r.json()

    async def confirm_email(self, data,
                            client: aiohttp.ClientSession):
        r = await client.post(url='https://api.rug.ai/v1/auth/email/verify',
                              data=json.dumps(data),
                              verify_ssl=False)
        # logger.debug(f"POST https://api.rug.ai/v1/auth/email/verify {data} / {await r.json()}")

        return await r.json()

    async def start(self, proxy: str | None = None) -> None:
        self.ref_code: str = choice(ref_codes)
        email_client: CreateClient = CreateClient(proxy)
        logger.debug(f"Get email - using: {proxy}")
        random_email: str = await email_client.get_email()
        logger.debug(f"Email: {random_email}")
        password = generate_password()

        data = {
            'username': random_email,
            'password': password,
            'referral_code': self.ref_code,
        }
        ua = UserAgent()
        user_agent = ua.getRandom
        async with aiohttp.ClientSession(connector=await get_connector(proxy=proxy),
                                         headers={
                                             'accept': 'application/json, text/plain, */*',
                                             'content-type': 'application/json',
                                             'user-agent': user_agent['useragent']
                                         }) as client:
            result_create = await self.register(data, client=client)
            if result_create['status_code'] == 200:
                logger.debug("Waiting for a letter in the mail...")

                confirm_code = await get_code(email_client, random_email)
                logger.debug(f"Waiting, the code - {confirm_code}")
                data['confirmation_code'] = confirm_code

                try:
                    result_account = await self.confirm_email(data, client=client)
                except Exception as e:
                    if "code=200" in e:
                        logger.warning("aiohttp.client_exceptions.ServerDisconnectedError - it seems to have worked ")


                async with aiofiles.open(file='registered.txt',
                                         mode='a',
                                         encoding='utf-8-sig') as file:
                    await file.write(f'{random_email}:{password}:{self.ref_code}:{proxy}\n')

                logger.success(f'Successfully registered account {random_email} | {self.ref_code} | Used proxy: {proxy}')


async def get_code(client, random_email):
    for attempt in range(3):
        try:
            messages: dict = await client.get_last_message_data(email=random_email)
            # logger.debug(messages)
            for message in messages:
                if not "Your One-Time Passcode" in message:
                    pass
                message_id: str = message['messageID']
                # logger.debug(message_id)
                if message_id == "ADSVPN":
                    time.sleep(10)
                else:
                    try:
                        message_text: str = await client.get_message(email=random_email,
                                                         message_id=message_id)
                        # logger.debug(message_text)

                        soup = BeautifulSoup(message_text, 'html.parser')
                        # Находим элемент, содержащий одноразовый пароль
                        paragraphs = soup.find_all('p')
                        for p in paragraphs:
                            otp_value = p.get_text().strip()
                            if re.match(r"^\d{6}$", otp_value):
                                return otp_value
                            else:
                                # logger.debug("No otp")
                                pass

                        # Извлекаем текст одноразового пароля)


                    except Exception as e:
                        logger.error(e)
                        # logger.debug(traceback.format_exc())
        except Exception as e:
            logger.error(f"Error with handling text email message - {e}")
            # logger.debug(traceback.format_exc())
            return False


async def start_reger(software_method: int,
                      proxy: str | None = None,
                      proxies_cycled: cycle | None = None,
                      private_key: str | None = None) -> None:
    match software_method:
        case 1:
            # while True:
            try:
                reg = Reger()
                await reg.start(proxy=proxy)


            except Exception as error:
                logger.error(f'Unexpected Error: {error}')
                logger.debug(traceback.format_exc())

            else:
                return