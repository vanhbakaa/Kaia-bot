import asyncio
from time import time
from urllib.parse import unquote

import aiohttp
from aiocfscrape import CloudflareScraper
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered, FloodWait
from pyrogram.raw.types import InputBotAppShortName
from pyrogram.raw.functions.messages import RequestAppWebView
from bot.core.agents import generate_random_user_agent
from bot.config import settings
import requests

from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers
from random import randint
from datetime import datetime, timedelta

api_auth = 'https://app.wallacy.io/spinky/api/x/auth-telegram-webapp'
api_claim = "https://app.wallacy.io/spinky/api/x/claim/"
api_checkin = "https://app.wallacy.io/spinky/api/x/checkin"
api_mining_data = "https://app.wallacy.io/spinky/api/collections/mining/records?page=1&perPage=500&skipTotal=1"
api_task_data = 'https://app.wallacy.io/spinky/api/collections/reward_tasks/records?page=1&perPage=500&skipTotal=1&filter=disabled%3Dfalse&sort=-created'
api_get_upgrade_data = 'https://app.wallacy.io/spinky/api/collections/upgrade_items/records?page=1&perPage=500&skipTotal=1'
api_upgrade = 'https://app.wallacy.io/spinky/api/x/upgrade'
api_spin_data = 'https://app.wallacy.io/spinky/api/collections/spins/records?page=1&perPage=500&skipTotal=1'
api_spin = 'https://app.wallacy.io/spinky/api/x/spin'

class Tapper:
    def __init__(self, tg_client: Client):
        self.tg_client = tg_client
        self.session_name = tg_client.name
        self.first_name = ''
        self.last_name = ''
        self.user_id = ''
        self.auth_token = ""
        self.last_claim = None
        self.last_checkin = None
        self.balace = 0

    async def get_tg_web_data(self, proxy: str | None) -> str:
        ref_param = settings.REF_LINK.split("=")[1]
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()
                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)

            while True:
                try:
                    peer = await self.tg_client.resolve_peer('kaiaplaybot')
                    break
                except FloodWait as fl:
                    fls = fl.value

                    logger.warning(f"<light-yellow>{self.session_name}</light-yellow> | FloodWait {fl}")
                    logger.info(f"<light-yellow>{self.session_name}</light-yellow> | Sleep {fls}s")

                    await asyncio.sleep(fls + 3)

            web_view = await self.tg_client.invoke(RequestAppWebView(
                peer=peer,
                app=InputBotAppShortName(bot_id=peer, short_name="app"),
                platform='android',
                write_allowed=True,
                start_param=ref_param
            ))

            auth_url = web_view.url
            tg_web_data = unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
            # print(tg_web_data)

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return tg_web_data

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"<light-yellow>{self.session_name}</light-yellow> | Unknown error during Authorization: "
                         f"{error}")
            await asyncio.sleep(delay=3)


    async def check_proxy(self, http_client: aiohttp.ClientSession, proxy: Proxy):
        try:
            response = await http_client.get(url='https://httpbin.org/ip', timeout=aiohttp.ClientTimeout(5))
            ip = (await response.json()).get('origin')
            logger.info(f"{self.session_name} | Proxy IP: {ip}")
            return True
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error}")
            return False


    def get_user_data(self, query_id, session: requests.Session):
        payload = {
            "initData": query_id
        }
        try:
            response = session.post(api_auth, json=payload)
            if response.status_code == 200:
                data_json = response.json()
                return data_json
            else:
                logger.error(f"Get user data failed. Status code: {response.status_code}")
        except Exception as e:
            logger.error(f"{self.session_name} cant get user data. Error: {e}")

    def claim(self, auth_token, session: requests.Session):
        payload = {
            "tokenSymbol": auth_token
        }
        headers['Authorization'] = auth_token
        try:
            response = session.post(api_claim, json=payload, headers=headers)
            if response.status_code == 200:
                data_json = response.json()
                self.last_claim = data_json['tran']['updated']
                logger.success(f"{self.session_name} | <green>Successfully claimed {data_json['tran']['amount']}.</green>")
            else:
                data_json = response.json()
                print(data_json)
                logger.error(f"{self.session_name} | <red>Claim failed. Status code: {response.status_code} </red>")
        except Exception as e:
            logger.error(f"{self.session_name} cant claim KP. Error: {e}")

    def checkin(self, auth_token, session: requests.Session):
        payload = {
            "taskId": "0ok0vh5i0vpx95r"
        }
        headers['Authorization'] = auth_token
        try:
            response = session.post(api_checkin, json=payload, headers=headers)
            if response.status_code == 200:
                logger.success(f"{self.session_name} | <green>Successfully claimed 4 KP.</green>")
            else:
                data_json = response.json()
                print(data_json)
                logger.error(f"{self.session_name} | <red>Check in failed. Status code: {response.status_code} </red>")
        except Exception as e:
            logger.error(f"{self.session_name} | Cant claim KP. Error: {e}")

    def fetch_data_mining(self, session: requests.Session):
        headers['Authorization'] = self.auth_token
        try:
            response = session.get(api_mining_data, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                data_json = response.json()
                print(data_json)
                logger.info(f"{self.session_name} | Failed to fetch data. Status code: {response.status_code}")
                return None
        except Exception as e:

            logger.error(f"{self.session_name} | Failed to fetch data. Error: {e}")
            return None

    def feth_data_task(self, session: requests.Session):
        headers['Authorization'] = self.auth_token
        try:
            response = session.get(api_task_data, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                data_json = response.json()
                print(data_json)
                logger.info(f"{self.session_name} | Failed to fetch tasks data. Status code: {response.status_code}")
                return None
        except Exception as e:

            logger.error(f"{self.session_name} | Failed to fetch tasks data. Error: {e}")

    def get_upgrade_data(self, session: requests.Session):
        headers['Authorization'] = self.auth_token
        try:
            response = session.get(api_get_upgrade_data, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                data_json = response.json()
                print(data_json)
                logger.info(f"{self.session_name} | Failed to fetch upgrades data. Status code: {response.status_code}")
                return None
        except Exception as e:

            logger.error(f"{self.session_name} | Failed to fetch tasks data. Error: {e}")

    def upgrade(self, upgrade_id, type, level, price, session: requests.Session):
        if type == "booster":
            txt = "Mining speed"
        else:
            txt = "Mining mutiplier"
        payload = {
            "itemId": upgrade_id
        }
        headers['Authorization'] = self.auth_token
        try:
            response = session.post(api_upgrade, json=payload, headers=headers)
            if response.status_code == 200:
                self.balace -= price
                logger.success(f"{self.session_name} | <green>Successfully upgraded {txt} to lvl {level} - Cost {price} KP</green>")
            else:
                data_json = response.json()
                print(data_json)
                logger.error(f"{self.session_name} | <red>Upgrade {txt} to lvl{level} failed. Status code: {response.status_code} </red>")
        except Exception as e:
            logger.error(f"{self.session_name} | Upgrade {txt} to lvl{level} failed. Error: {e}")

    def get_spin_data(self, session: requests.Session):
        headers['Authorization'] = self.auth_token
        try:
            response = session.get(api_spin_data,headers=headers)
            if response.status_code == 200:
                logger.info(f"{self.session_name} | <green>Get spin data successfully</green>")
                return response.json()
            else:
                logger.error(f"{self.session_name} | <red>Get spin data failed. Status code: {response.status_code} </red>")
                return None
        except Exception as e:
            logger.error(f"{self.session_name} | Get spin data failed. Error: {e}")
            return None

    def spin(self, spinId, spinToken, session: requests.Session):
        payload = {
            "spinId": spinId,
            "spinToken": spinToken
        }
        headers['Authorization'] = self.auth_token
        try:
            response = session.post(api_spin, json=payload, headers=headers)
            if response.status_code == 200:
                json_data = response.json()
                logger.success(f"{self.session_name} | <green>Spin successfully {json_data['reward']['name']}</green>")
            else:
                data_json = response.json()
                print(data_json)
                logger.error(f"{self.session_name} | <red>Spin failed. Status code: {response.status_code} </red>")
        except Exception as e:
            logger.error(f"{self.session_name} | Spin failed. Error: {e}")

    async def run(self, proxy: str | None) -> None:
        access_token_created_time = 0
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None

        headers["User-Agent"] = generate_random_user_agent(device_type='android', browser_type='chrome')
        http_client = CloudflareScraper(headers=headers, connector=proxy_conn)
        session = requests.Session()

        if proxy:
            proxy_check = await self.check_proxy(http_client=http_client, proxy=proxy)
            if proxy_check:
                proxy_type = proxy.split(':')[0]
                proxies = {
                    proxy_type: proxy
                }
                session.proxies.update(proxies)
                logger.info(f"{self.session_name} | bind with proxy ip: {proxy}")

        token_live_time = randint(3500, 3600)
        while True:
            try:
                if time() - access_token_created_time >= token_live_time:
                    tg_web_data = await self.get_tg_web_data(proxy=proxy)
                    user_data = self.get_user_data(tg_web_data, session)
                    logger.info(f"{user_data['record']['name']} logged in...")
                    self.balace = user_data['record']['balance']
                    logger.info(f"{self.session_name} | Balance: <yellow>{user_data['record']['balance']} | Top {user_data['record']['topPercent']}%</yellow>")
                    self.auth_token = user_data['token']
                    access_token_created_time = time()
                    token_live_time = randint(3500, 3600)

                if settings.AUTO_SPIN:
                    can_spin = True
                    while can_spin:
                        spin_data = self.get_spin_data(session)
                        if spin_data:
                            for spin in spin_data['items']:
                                if spin['isEligible']:
                                    if spin['level'] == 1 and settings.LVL_TO_SPIN == 1:
                                        logger.info(f"{self.session_name} | Attemp to spin at top 1k - spend 60 KP...")
                                    elif spin['level'] == 2 and settings.LVL_TO_SPIN == 2:
                                        logger.info(f"{self.session_name} | Attemp to spin at top 3k - spend 40 KP...")
                                    elif spin['level'] == 3 and settings.LVL_TO_SPIN == 3:
                                        logger.info(f"{self.session_name} | Attemp to spin at top 5k - spend 20 KP...")
                                    elif spin['level'] == 4 and settings.LVL_TO_SPIN == 4:
                                        logger.info(f"{self.session_name} | Attemp to spin at top >5k - spend 10 KP...")
                                    if spin['remainingSpin'] > 0 and settings.LVL_TO_SPIN >= spin['level']:
                                        self.spin(spin['id'], spin['token'], session)
                                    else:
                                        logger.info(f"{self.session_name} | No spin left...")
                        else:
                            break

                        await asyncio.sleep(randint(5,10))


                if settings.AUTO_UPGRADE:
                    upgrade_data = self.get_upgrade_data(session)
                    data = self.fetch_data_mining(session)
                    mining_speed = data['items'][0]['items'][1]
                    mining_multi = data['items'][0]['items'][2]
                    if upgrade_data:
                        for upgrade in upgrade_data['items']:
                            if self.balace < upgrade['price']:
                                continue
                            if upgrade['type'] == "battery":
                                continue
                            if upgrade['type'] == "booster" and upgrade['level'] == (mining_speed['level']+1):
                                self.upgrade(upgrade['id'], upgrade['type'], upgrade['level'], upgrade['price'],session)
                            elif upgrade['type'] == "multiplier" and upgrade['level'] == (mining_multi['level']+1):
                                self.upgrade(upgrade['id'], upgrade['type'], upgrade['level'], upgrade['price'], session)

                check_in_data = self.feth_data_task(session)
                sleep_2 = 0
                if check_in_data:
                    if check_in_data['items'][-1]['isCompleted'] is False:
                        self.checkin(self.auth_token, session)
                    else:
                        initial_time_str = check_in_data['items'][-1]['nextCheckinTime']
                        target_time = datetime.strptime(initial_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')
                        current_time = datetime.utcnow()
                        time_left = target_time - current_time
                        seconds_left = time_left.total_seconds()
                        sleep_ = randint(10, 20)
                        sleep_2 = seconds_left+sleep_

                data = self.fetch_data_mining(session)
                if data is None:
                    sleep_ = randint(100, 300)
                    logger.info(f"{self.session_name} | Sleep {sleep_}")
                    await asyncio.sleep(sleep_)
                else:
                    if data['items'][0]['isClaimable']:
                        self.claim(self.auth_token, session)
                    else:
                        initial_time_str = data['items'][0]['started_at']
                        initial_time = datetime.strptime(initial_time_str, '%Y-%m-%d %H:%M:%S.%fZ')
                        current_time = datetime.utcnow()
                        target_time = initial_time + timedelta(minutes=data['items'][0]['currentBatteryCapacity'])
                        time_left = target_time - current_time
                        seconds_left = time_left.total_seconds()
                        sleep_ = randint(10, 20)
                        sleep_time = seconds_left + sleep_
                        real_sleep = min(sleep_time, sleep_2)
                        logger.info(f"{self.session_name} | Next claim in {real_sleep}s. Sleep {real_sleep}s...")
                        await asyncio.sleep(real_sleep)

                sleep_ = randint(10, 20)
                logger.info(f"{self.session_name} | Sleep {sleep_}s...")
                await asyncio.sleep(sleep_)

            except InvalidSession as error:
                raise error

            except Exception as error:
                logger.error(f"{self.session_name} | Unknown error: {error}")
                await asyncio.sleep(delay=randint(60, 120))

async def run_tapper(tg_client: Client, proxy: str | None):
    try:
        sleep_ = randint(1, 15)
        logger.info(f"{tg_client.name} | start after {sleep_}s")
        await asyncio.sleep(sleep_)
        await Tapper(tg_client=tg_client).run(proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
