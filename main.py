import os, logging, requests
from aiogram import Bot, Dispatcher, types, executor
from bs4 import BeautifulSoup
from aiogram.types import InputMediaPhoto

API_TOKEN = os.getenv('API_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.reply("Привет! Пришли ссылку на товар с Wildberries ✨")

@dp.message_handler()
async def handle_link(message: types.Message):
    url = message.text.strip()
    if "wildberries.ru" not in url:
        return await message.reply("Это не ссылка на Wildberries.")

    try:
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else 'Товар'
        price = soup.select_one('span.price-block__price').text.strip()
        old_tag = soup.select_one('del.price-block__old-price')
        old = old_tag.text.strip() if old_tag else ''
        desc = soup.find('p').text.strip() if soup.find('p') else ''
        imgs = [("https:"+i['src'] if i['src'].startswith("//") else i['src'])
                for i in soup.select('img[src*="images"]')[:3]]
        post = f"**{title}**\n💰 {price} ({old})\n\n📋 {desc}\n\n🔗 {url}"
        
        if imgs:
            media = [InputMediaPhoto(u) for u in imgs]
            media[0].caption = post
            media[0].parse_mode = "Markdown"
            await bot.send_media_group(message.chat.id, media)
        else:
            await message.reply(post, parse_mode="Markdown")

    except Exception as e:
        logging.exception(e)
        await message.reply("Ошибка при обработке.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
