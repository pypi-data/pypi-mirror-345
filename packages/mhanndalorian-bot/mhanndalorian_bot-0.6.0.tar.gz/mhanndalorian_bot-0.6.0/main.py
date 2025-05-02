"""
Test script for MBot
"""

from __future__ import annotations, absolute_import
import asyncio
import logging
from pprint import pprint as pp

from mhanndalorian_bot import API, Registry, EndPoint


class LoggingFormatter(logging.Formatter):
    """Custom logging formatter class"""

    def format(self, record):
        log_message_format = \
            '{asctime} | {levelname} | {name} | {module} : {funcName}() [{lineno:}] | {message}'
        formatter = logging.Formatter(log_message_format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setFormatter(LoggingFormatter())
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)


api = API(api_key="some_test_key", allycode="123456789")
api.sign(method="POST", endpoint=EndPoint.INVENTORY, payload={"payload": {"allyCode": "123456789"}})

allycode = '314927874'
allycode2 = '245866537'
api_key = 'usergeneratedoNtGtKG0YW6sLSj1Q12Q7hOCVhTAgvd0xMexdLK4qZZhnQbSO1'
discord_id = '344006512546545667'
discord_id2 = '730760587864178710'

# api = API(api_key, allycode)
# reg = Registry(api_key, allycode)

# resp = api.fetch_data(endpoint=EndPoint.INVENTORY,)

# if resp.status_code == 200:
#     resp_data = resp.json()
#     print(sorted(list(resp_data['inventory'].keys())))
# else:
#     print(f"{resp.status_code}: {resp.text}")

reg_resp = reg.fetch_player(allycode,)

if isinstance(reg_resp, dict) and 'allyCode' in reg_resp and 'discordId' in reg_resp:
    print("Registry fetch_user() verified.")

print("Registry register_user() test:")
reg_resp = reg.register_player(discord_id2, allycode2)
pp(reg_resp)

if isinstance(reg_resp, dict):
    print(reg_resp['unlockedPlayerPortrait'])
    print(reg_resp['unlockedPlayerTitle'])
    print("Registry register_user() verified.")

reg_resp = reg.verify_player(discord_id2, allycode2)
print(f"Registry verify_user(): {reg_resp}")


async def main():
    # reg = Registry(api_key, allycode)

    api = API(api_key, allycode)

    fetch_data_resp = await api.fetch_data_async(EndPoint.INVENTORY)

    if isinstance(fetch_data_resp, dict):
        if 'msg' in fetch_data_resp:
            # An unexpected error occurred
            print(f"An unexpected error occurred: {fetch_data_resp}")
        elif 'inventory' in fetch_data_resp:
            material: list = fetch_data_resp['inventory']['material']
            currency: list = fetch_data_resp['inventory']['currencyItem']
            equipment: list = fetch_data_resp['inventory']['equipment']
            unequipped_mods: list = fetch_data_resp['inventory']['unequippedMod']
        else:
            raise RuntimeError("Not sure what happened.")


    # Returns 'None' if player does not exist in the registry
    fetch_resp = await reg.fetch_player_async(allycode)

    if isinstance(fetch_resp, dict):
        if 'msg' in fetch_resp:
            # An unexpected error occurred
            print(f"An unexpected error occurred: {fetch_resp}")
        else:
            player_allycode = fetch_resp['allyCode']
            player_discord_id = fetch_resp['discordId']


    register_resp = await reg.register_player_async(discord_id, allycode2)
    pp(register_resp)
    pp(register_resp.text)
    if register_resp.status_code == 200:
        register_data = register_resp.json()
        pp(register_data)
        print(register_data['unlockedPlayerPortrait'])
        print(register_data['unlockedPlayerTitle'])
        print("Registry async register_user() verified.")

    # verify_resp = await reg.verify_player_async(discord_id, allycode2,)  # print(f"Registry async verify_user(): {verify_resp}")


if __name__ == '__main__':
    asyncio.run(main())
