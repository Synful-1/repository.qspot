import os
import sys
import urllib.request
import zipfile
import xbmc
import xbmcgui
import xbmcvfs

# Direct Dropbox Link
DROPBOX_URL = "https://www.dropbox.com/scl/fi/5ugwuc1qzivekgcniy7nw/Build.zip?rlkey=70gimrla0m7s5218g5m39yar4&dl=1"

# Kodi Home Directory Path
HOME_DIR = xbmcvfs.translatePath('special://home/')
TEMP_ZIP = os.path.join(HOME_DIR, 'temp_build.zip')

def download_build(url, dest_path, progress_dialog):
    """Downloads the backup ZIP file while updating the progress status."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req) as response, open(dest_path, 'wb') as out_file:
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            chunk_size = 1024 * 1024  # 1 MB chunks

            while True:
                if progress_dialog.iscanceled():
                    return False
                
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                    
                downloaded += len(chunk)
                out_file.write(chunk)

                if total_size > 0:
                    percent = int((downloaded / total_size) * 100)
                    mb_downloaded = round(downloaded / (1024 * 1024), 1)
                    mb_total = round(total_size / (1024 * 1024), 1)
                    progress_dialog.update(
                        percent, 
                        f"Downloading Build... {percent}%\n{mb_downloaded} MB / {mb_total} MB"
                    )
                else:
                    mb_downloaded = round(downloaded / (1024 * 1024), 1)
                    progress_dialog.update(50, f"Downloading Build...\n{mb_downloaded} MB downloaded")
                    
        return True
    except Exception as e:
        xbmcgui.Dialog().ok("Download Error", f"Failed to download build:\n{str(e)}")
        return False

def extract_build(zip_path, dest_dir, progress_dialog):
    """Extracts the backup ZIP to special://home/ with progress status updates."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            members = zip_ref.infolist()
            total_files = len(members)

            for index, member in enumerate(members):
                if progress_dialog.iscanceled():
                    return False

                zip_ref.extract(member, dest_dir)
                percent = int(((index + 1) / total_files) * 100)
                progress_dialog.update(
                    percent, 
                    f"Extracting Files... {percent}%\n({index + 1} / {total_files} files)"
                )
        return True
    except Exception as e:
        xbmcgui.Dialog().ok("Extraction Error", f"Failed to extract build:\n{str(e)}")
        return False

def force_close_kodi():
    """Forces Kodi process termination to preserve restored configuration files."""
    xbmcgui.Dialog().ok("Restore Complete", "Build installed! Kodi will now force close to complete setup.")
    
    # Platform-specific process kill commands
    if os.name == 'posix':  # Android, Linux, macOS
        os.system('killall -9 kodi.bin')
        os.system('killall -9 Kodi')
        os.system('killall -9 org.xbmc.kodi')
    elif os.name == 'nt':     # Windows
        os.system('taskkill /f /im kodi.exe')

    # Hard Python exit fallback
    os._exit(1)

def run_wizard():
    dp = xbmcgui.DialogProgress()
    dp.create("Restore Wizard", "Connecting to Dropbox...")

    try:
        # Step 1: Download
        if not download_build(DROPBOX_URL, TEMP_ZIP, dp):
            dp.close()
            return

        # Step 2: Extract
        dp.update(0, "Preparing to extract build...")
        if not extract_build(TEMP_ZIP, HOME_DIR, dp):
            dp.close()
            if os.path.exists(TEMP_ZIP):
                os.remove(TEMP_ZIP)
            return

        # Step 3: Clean up downloaded ZIP
        dp.close()
        if os.path.exists(TEMP_ZIP):
            os.remove(TEMP_ZIP)

        # Step 4: Force close Kodi
        force_close_kodi()

    except Exception as e:
        dp.close()
        if os.path.exists(TEMP_ZIP):
            os.remove(TEMP_ZIP)
        xbmcgui.Dialog().ok("Wizard Error", f"An unexpected error occurred:\n{str(e)}")

if __name__ == '__main__':
    run_wizard()