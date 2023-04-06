from io import BytesIO
from aiohttp import ClientSession
from base.module import command, BaseModule
from pyrogram.types import Message



url = "https://api.qrserver.com/v1/create-qr-code/?data=" \
      "{}&size=512x512&charset-source=UTF-8&charset-target=UTF-8&ecc=L&color=0-0-0&bgcolor=255-255-255&margin=1" \
      "&qzone=1&format=png"
url2 = "https://api.qrserver.com/v1/read-qr-code/?outputformat=json"


class QrMod(BaseModule):
    @command("readqr")
    async def readqrcode(self, _, message: Message):
        """Read Qr-Code"""
        use = self.S["readqr"]["usg"]
        decr = self.S["readqr"]["decrypted"]
        failed = self.S["readqr"]["fail"]
        readerr = self.S["errors"]['error']
        try:
            if message.photo:
                filename = await message.download('temp.png')
            elif message.text:
                if not message.reply_to_message:
                    return await message.reply(use)
                filename = await message.reply_to_message.download('temp.png')
            else:
                return await message.reply(use)

            async with ClientSession() as session:
                async with session.post(url2, data={'file': open(filename, 'rb').read()}) as response:
                    json = await response.json()
                    text = json[0]["symbol"][0]["data"]
                    if not text:
                        return await message.reply(failed)
                    return await message.reply(f'{decr}\n<code>{text}</code>')
        except Exception as e:
            return await message.reply(f"{readerr} {str(e)}")

    @command("genqr")
    async def genqrcode(self, _, message: Message):
        """Generate Qr-code"""
        usegen = self.S["genqr"]["genuse"]
        generr = self.S["errors"]['error']
        if len(message.text.split()) < 2:
            return await message.reply(usegen)
        data = message.text.split(maxsplit=1)[1]
        try:
            async with ClientSession() as session:
                async with session.get(url.format(data)) as response:
                    qrcode = BytesIO(await response.read())
                    qrcode.name = 'qrcode.png'
                    qrcode.seek(0)
                    await message.reply_photo(qrcode)
                    return await message.delete()
        except Exception as e:
            return await message.reply(f"{readerr} {str(e)}")
