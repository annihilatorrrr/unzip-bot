# Copyright (c) 2022 EDM115
import os
import pathlib
import re
import shutil
import subprocess
from asyncio import sleep
from time import time

from pyrogram.errors import FloodWait

from config import Config
from unzipper import LOGGER
from unzipper import unzipperbot
from unzipper.helpers.database import get_upload_mode
from unzipper.helpers.unzip_help import extentions_list
from unzipper.helpers.unzip_help import progress_for_pyrogram
from unzipper.modules.bot_data import Messages
from unzipper.modules.ext_script.custom_thumbnail import thumb_exists


# To get video duration and thumbnail
async def run_shell_cmds(command):
    run = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    return run.stdout.read()[:-1].decode("utf-8")


# Get file size
async def get_size(doc_f):
    try:
        return os.stat(doc_f).st_size
    except:
        return 0


# Send file to a user
async def send_file(unzip_bot, c_id, doc_f, query, full_path, log_msg, split):
    try:
        ul_mode = await get_upload_mode(c_id)
        if split:
            fname = doc_f
            fext = doc_f.split("/")[-1].casefold()
        else:
            fname = os.path.basename(doc_f)
            fext = (pathlib.Path(os.path.abspath(doc_f)).suffix).casefold()
        thumbornot = await thumb_exists(c_id)
        upmsg = await unzip_bot.send_message(c_id, "`Processing… ⏳`")
        if ul_mode == "media" and fext in extentions_list["audio"]:
            if thumbornot:
                thumb_image = f"{Config.THUMB_LOCATION}/{str(c_id)}.jpg"
                await unzip_bot.send_audio(
                    chat_id=c_id,
                    audio=doc_f,
                    caption=Messages.EXT_CAPTION.format(fname),
                    thumb=thumb_image,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"**Trying to upload {fname}… Please wait** \n",
                        upmsg,
                        time(),
                    ),
                )
            else:
                await unzip_bot.send_audio(
                    chat_id=c_id,
                    audio=doc_f,
                    caption=Messages.EXT_CAPTION.format(fname),
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"**Trying to upload {fname}… Please wait** \n",
                        upmsg,
                        time(),
                    ),
                )
        elif ul_mode == "media" and fext in extentions_list["photo"]:
            # impossible to use a thumb here :(
            await unzip_bot.send_photo(
                chat_id=c_id,
                photo=doc_f,
                caption=Messages.EXT_CAPTION.format(fname),
                progress=progress_for_pyrogram,
                progress_args=(
                    f"**Trying to upload {fname}… Please wait** \n",
                    upmsg,
                    time(),
                ),
            )
        elif ul_mode == "media" and fext in extentions_list["video"]:
            vid_duration = await run_shell_cmds(
                f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {doc_f}"
            )
            if thumbornot:
                thumb_image = f"{Config.THUMB_LOCATION}/{str(c_id)}.jpg"
                await unzip_bot.send_video(
                    chat_id=c_id,
                    video=doc_f,
                    caption=Messages.EXT_CAPTION.format(fname),
                    duration=int(
                        vid_duration) if vid_duration.isnumeric() else 0,
                    thumb=thumb_image,
                    supports_streaming=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"**Trying to upload {fname}… Please wait** \n",
                        upmsg,
                        time(),
                    ),
                )
            else:
                thmb_pth = (
                    f"{Config.THUMB_LOCATION}/thumbnail_{os.path.basename(doc_f)}.jpg"
                )
                if os.path.exists(thmb_pth):
                    os.remove(thmb_pth)
                thumb = await run_shell_cmds(
                    f"ffmpeg -ss 00:00:01.00 -i {doc_f} -vf 'scale=320:320:force_original_aspect_ratio=decrease' -vframes 1 {thmb_pth}"
                )
                await unzip_bot.send_video(
                    chat_id=c_id,
                    video=doc_f,
                    caption=Messages.EXT_CAPTION.format(fname),
                    duration=int(
                        vid_duration) if vid_duration.isnumeric() else 0,
                    thumb=str(thumb),
                    supports_streaming=True,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        f"**Trying to upload {fname}… Please wait** \n",
                        upmsg,
                        time(),
                    ),
                )
                os.remove(thmb_pth)
        elif thumbornot:
            thumb_image = f"{Config.THUMB_LOCATION}/{str(c_id)}.jpg"
            await unzip_bot.send_document(
                chat_id=c_id,
                document=doc_f,
                thumb=thumb_image,
                caption=Messages.EXT_CAPTION.format(fname),
                progress=progress_for_pyrogram,
                progress_args=(
                    f"**Trying to upload {fname}… Please wait** \n",
                    upmsg,
                    time(),
                ),
            )
        else:
            await unzip_bot.send_document(
                chat_id=c_id,
                document=doc_f,
                caption=Messages.EXT_CAPTION.format(fname),
                progress=progress_for_pyrogram,
                progress_args=(
                    f"**Trying to upload {fname}… Please wait** \n",
                    upmsg,
                    time(),
                ),
            )
        await upmsg.delete()
        os.remove(doc_f)
    except FloodWait as f:
        await sleep(f.value)
        return await send_file(unzip_bot, c_id, doc_f, query, full_path, log_msg, split)
    except FileNotFoundError:
        return await query.answer("Sorry ! I can't find that file 💀", show_alert=True)
    except BaseException as e:
        LOGGER.warning(e)
        shutil.rmtree(full_path)


async def send_url_logs(unzip_bot, c_id, doc_f, source):
    try:
        u_file_size = os.stat(doc_f).st_size
        if Config.TG_MAX_SIZE < int(u_file_size):
            return await unzip_bot.send_message(
                chat_id=c_id, text="URL file is too large to send in telegram 😥"
            )
        fname = os.path.basename(doc_f)
        await unzip_bot.send_document(
            chat_id=c_id,
            document=doc_f,
            caption=Messages.LOG_CAPTION.format(fname, source),
        )
    except FloodWait as f:
        await sleep(f.value)
        return send_url_logs(unzip_bot, c_id, doc_f, source)
    except FileNotFoundError:
        await unzip_bot.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text="Archive has gone from servers before uploading 😥",
        )
    except BaseException:
        pass


async def merge_splitted_archives(user_id, path):
    cmd = f"cd {path} && cat * > MERGED_{user_id}.zip"
    await run_shell_cmds(cmd)


# Function to remove basic markdown characters from a string
async def rm_mark_chars(text: str):
    return re.sub("[*`_]", "", text)


# Function to answer queries
async def answer_query(
    query, message_text: str, answer_only: bool = False, unzip_client=None, buttons=None
):
    try:
        if answer_only:
            await query.answer(await rm_mark_chars(message_text), show_alert=True)
        else:
            await query.message.edit(message_text, reply_markup=buttons)
    except:
        if unzip_client:
            await unzip_client.send_message(
                chat_id=query.message.chat.id, text=message_text, reply_markup=buttons
            )
        else:
            await unzipperbot.send_message(
                chat_id=query.message.chat.id, text=message_text, reply_markup=buttons
            )
