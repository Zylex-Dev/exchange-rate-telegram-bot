from aiogram import Bot

from bot.main import get_bot
from utils.db.user import get_all_users
from db.session import async_session
from utils.log import logger


async def send_message(user, bot: Bot, message_text: str):
    try:
        await bot.send_message(chat_id=user.id, text=message_text)
        logger.info(f"Message successfully sent to user {user.id}")
    except Exception as e:
        logger.error(f"Failed to send message to user {user.id}: {e}")


async def send_message_to_all_users(message_text: str) -> None:
    logger.info("Starting the process of sending messages to all users.")

    bot: Bot = get_bot()

    async with async_session() as session:
        try:
            users = await get_all_users(session)
            logger.info(f"Retrieved {len(users)} users for message delivery.")

            tasks = [
                asyncio.create_task(send_message(user, bot, message_text))
                for user in users
            ]

            await asyncio.gather(*tasks)
            logger.info("All messages have been successfully sent.")
        except Exception as e:
            logger.error(f"Error during user retrieval or message sending: {e}")


if __name__ == "__main__":
    import asyncio

    message_text = """```
📢 Patch Notes: New Bot Features and Updates  
    
🔔 Notifications Management  

- 🛠 New Notification Settings Menu:  
  Manage your preferences with ease! Choose which services to receive alerts from or toggle them off entirely.  
  🧭 How to access: Use the Notifications button in the bot menu.  

- 🗂 Service-Specific Alerts:  
  - Enable or disable notifications for:  
    - 💳 Gazprombank (GZ)  
    - 🌐 Google Finance  
    - 🏦 Central Bank of Russia (CBR)  
  - Stay updated when exchange rates meet your thresholds!  

- 🚦 Quick Disable Option:  
  Toggle all notifications off with a single tap for maximum convenience.  

⚙️ Custom Thresholds  

- 🎯 Set Your Own Limits:  
  - Customize thresholds for each service: Gazprombank, Google Finance, and CBR.  
  - Alerts are triggered when the exchange rate falls below your chosen value.  
  
- 🔄 Easy Update Process:  
  - Select a service and input the new threshold value.  
  - ✅ The bot will confirm the update and display the current settings.  

🎯 How to Get Started?  
1. ⚙️ Open the Notifications Menu.  
2. 🎛 Customize your alerts and thresholds.  
3. 📩 Stay informed with timely exchange rate updates!  


🎉 Thank you for using our bot!  
💬 For questions or feedback, feel free to contact us anytime.  
```
    """
    asyncio.run(send_message_to_all_users(message_text))
