import scanning as sc
from utils import new_org_message, new_data_message
from dotenv import load_dotenv
import os
from telegram import Bot
import asyncio
import logging
import pandas as pd
from reporting import send_email_report


load_dotenv()
channel_username = os.getenv("CHANNEL_USERNAME")
bot_token = os.getenv("BOT_TOKEN")
ckan_url = os.getenv("CKAN_URL")
pers_path = os.getenv("PERS_PATH")
missing_path = "missing_data.json"
sender = os.getenv("SENDER_EMAIL")
sender_pass=os.getenv("EMAIL_PASS")
receivers= os.getenv("RECEIVERS")

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def send_update(message):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=channel_username, text=message,parse_mode="MarkdownV2")


def main(link_ckan, file_path):
        data_dict = sc.get_current_datasets(link_ckan)
        org_list = sc.get_current_orgs(link_ckan)
        updates = sc.scan_updates(data_dict, org_list, file_path,missing_path, link_ckan)
        logger.info("Se terminaron de escanear los datos")
        # Si no hay datos nuevos termina el proceso, no compara organizaciones.
        if not isinstance(updates, pd.DataFrame):
            logger.info("No hay novedades, terminando proceso")
            return "No hay nuevos datos en el portal"
        else:
            org_updates = sc.scan_organizations(org_list, file_path)
            new_org_names = [org["name"] for org in org_updates if org.get("new") is True]
            org_in_data = updates['org'].tolist()
            org_inter = list(set(new_org_names) & set(org_in_data))
            if org_inter:
                logger.info("Hay nodos nuevos con data")
                text = new_org_message(org_updates, org_inter, link_ckan)
                for alias in org_inter:
                    for element in org_updates:
                        if element['name'] == alias:
                            element['new'] = False

                sc.save_ckan_state(data_dict, org_updates, file_path)
                logger.info("Mandando mensaje por nuevos nodos")
                return asyncio.run(send_update(text))
            text = new_data_message(updates,org_updates)
            sc.save_ckan_state(data_dict, org_updates, file_path)
            logger.info("Mandando mensaje por nuevos datasets")
            if isinstance(text,list):
                for element in text:
                    asyncio.run(send_update(element))
            else:
               return asyncio.run(send_update(text))



if __name__ == "__main__":
    try:
        main(ckan_url, pers_path)
        logger.info(f"SENDER: {sender}")
        logger.info(f"RECEIVERS: {receivers}")
        send_email_report(
            sender_email=sender,
            sender_password= sender_pass,
            recipient_email=receivers,
            subject='Telegram Bot Report',
            body='El bot corrió correctamente',
        )
    except Exception as e:
        send_email_report(
            sender_email=sender,
            sender_password=sender_pass,
            recipient_email=receivers,
            subject='Error - Telegram Bot Report',
            body=f'El bot no corrió correctamente:{e}',
        )
