import os
import shutil
import urllib.request
import zipfile

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs

ADDON = xbmcaddon.Addon()

# CHANGE THIS TO YOUR DROPBOX DIRECT LINK
DROPBOX_URL = "https://www.dropbox.com/scl/fi/ocificu13iqk6gef8k6ue/Build1.zip?rlkey=wn0oioxxqdgadhv5hikwuvxg0&st=if2907rh&dl=1"

dialog = xbmcgui.Dialog()

temp_dir = xbmcvfs.translatePath("special://temp/")
home_dir = xbmcvfs.translatePath("special://home/")

zip_path = os.path.join(temp_dir, "restore_build.zip")


def download_build():
    dp = xbmcgui.DialogProgress()
    dp.create("Restore Build", "Downloading build...")

    try:
        urllib.request.urlretrieve(DROPBOX_URL, zip_path)

        dp.close()

        if not os.path.exists(zip_path):
            raise Exception("ZIP download failed")

        return True

    except Exception as e:
        dp.close()
        dialog.ok("Error", str(e))
        return False


def extract_build():
    dp = xbmcgui.DialogProgress()
    dp.create("Restore Build", "Extracting build...")

    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            members = z.infolist()
            total = len(members)

            for count, member in enumerate(members):
                percent = int((count / total) * 100)
                dp.update(percent, member.filename)

                target = os.path.join(home_dir, member.filename)

                if member.is_dir():
                    os.makedirs(target, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target), exist_ok=True)

                    with z.open(member) as source:
                        with open(target, "wb") as dest:
                            shutil.copyfileobj(source, dest)

        dp.close()
        return True

    except Exception as e:
        dp.close()
        dialog.ok("Extraction Error", str(e))
        return False


def main():

    confirm = dialog.yesno(
        "Restore Build",
        "This will overwrite files in your Kodi installation.",
        "Continue?"
    )

    if not confirm:
        return

    if not download_build():
        return

    if not extract_build():
        return

    try:
        os.remove(zip_path)
    except:
        pass

    dialog.ok(
        "Success",
        "Build restored successfully.",
        "Please restart Kodi."
    )

    xbmc.executebuiltin("RestartApp")


if __name__ == "__main__":
    main()