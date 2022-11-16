import os
import re
import urllib.request

from aiogram import Dispatcher, Bot, executor, types
from zip_unpacking.unpacking import Unpaking
from up_load_video_youtube_data_api.main import Video_upload
from tokens import config

TOKEN = config.TOKEN
GET_ZIPFILE = False


bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await bot.send_message(message.chat.id, 'Привет!\nЯ бот который удалённо выкладывает видео на ютуб\nПропиши команду /send_video_upload и отправь архив с файлми: description.txt(описание), title.txt(заголовок видео), file.mp4(видео)')


@dp.message_handler(commands=['send_video_upload'], commands_prefix='!/')
async def chek_zip_fle(msg: types.Message):
    await bot.send_message(msg.chat.id, 'Теперь отправьте .zip файл.')

    @dp.message_handler(content_types=['document'])
    async def scan_message(msg: types.Message):

        document_id = msg.document.file_id
        file_info = await bot.get_file(document_id)
        fi = file_info.file_path
        name = msg.document.file_name

        try:
            urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}',f'main_zipfile_data/{name}')
        except:
            os.mkdir('main_zipfile_data')
            urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}', f'main_zipfile_data/{name}')

        try:
            urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}',f'set_data_zip_wl/data/{name}')
        except:
            os.mkdir('set_data_zip_wl/data')
            urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}', f'set_data_zip_wl/data/{name}')

        await bot.send_message(msg.from_user.id, 'Файл успешно сохранён')


        unzip = Unpaking(f'main_zipfile_data/{name}')
        unzip.unpaking_zip(file_name=name, file_path=f'main_zipfile_data/un_packing_zip')
        content = unzip.get_content_file(f'main_zipfile_data/un_packing_zip/{name}', unzip.get_info())

        content_title = content[re.findall(r'title.\w+', ", ".join(unzip.get_file_name()))[0]]['content']
        content_desc = content[re.findall(r'description.\w+', ", ".join(unzip.get_file_name()))[0]]['content']
        f = [i for i in unzip.get_file_name() if '.mp4' in i]
        content_video_path = f'main_zipfile_data/un_packing_zip/{name}/{f[0]}'

        print('title: ' + str(content_title) + '\n' + 'desc: ' + str(content_desc) + '\n' + 'path: ' + str(content_video_path))

        await bot.send_message(msg.from_user.id, 'Файл загружается, подождите!')
        video_upload = Video_upload(content_video_path, content_title, content_desc)
        video_upload.video_upload()
        await bot.send_message(msg.from_user.id, 'Файл загружен! Поздравляю!!!👏👏👏\nТеперь вы можете открыть доступ к этому видео на youtube.')
        print('Video has been uploading!!!')


if __name__=='__main__':
    executor.start_polling(dp, skip_updates=False)