# ---------------------------------------
# --- GEREKLİ MODÜLLERİ İMPORT EDİYORUZ ---
# ---------------------------------------

import ssl
import certifi
import os
import time
import json
import random
import threading
import warnings
import soundcard as sc
import soundfile as sf
from mtranslate import translate
import ollama
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import speech_recognition as sr

# ---------------------------------------
# --- UYARILARI KAPATIYORUZ ---
# ---------------------------------------

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

# ---------------------------------------
# --- SABİT DEĞİŞKENLERİ TANIMLIYORUZ ---
# ---------------------------------------

API_KEY = "374giayfaud738q"
kullanici_key = None

SETTINGS_PATH = "data.json"
MODEL_PATH = "model.json"
SYSTEM_PROMPT_PATH = "system_prompt.json"
PROFILS_PATH = "profils.json"
AKTIF_PATH = "aktif_profiller.json"

INSTAGRAM_PROFILS_PATH = "instagram_profils.json"
INSTAGRAM_AYARLAR_PATH = "instagram_ayarlar.json"

aktif_threadler = []

# ---------------------------------------
# --- VERİ KAYDETME VE YÜKLEME FONKSİYONLARI ---
# ---------------------------------------

def kaydet_aktif_threadler(liste):
    with open(AKTIF_PATH, "w", encoding="utf-8") as f:
        json.dump({"aktif": liste}, f)

def yukle_aktif_threadler():
    if os.path.exists(AKTIF_PATH):
        with open(AKTIF_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("aktif", [])
    return []

def kaydet_ayarlar(data):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)

def yukle_ayarlar():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def kaydet_model(model):
    with open(MODEL_PATH, "w", encoding="utf-8") as f:
        json.dump({"model": model}, f)

def yukle_model():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("model", None)
    return None

def kaydet_profil_sayaci(sayac):
    with open(PROFILS_PATH, "w", encoding="utf-8") as f:
        json.dump({"sayac": sayac}, f)

def yukle_profil_sayaci():
    if os.path.exists(PROFILS_PATH):
        with open(PROFILS_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("sayac", 1)
    return 1

def kaydet_instagram_profiller(liste):
    with open(INSTAGRAM_PROFILS_PATH, "w", encoding="utf-8") as f:
        json.dump({"profiller": liste}, f)

def yukle_instagram_profiller():
    if os.path.exists(INSTAGRAM_PROFILS_PATH):
        with open(INSTAGRAM_PROFILS_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("profiller", [])
    return []

def kaydet_instagram_ayarlar(data):
    with open(INSTAGRAM_AYARLAR_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)

def yukle_instagram_ayarlar():
    if os.path.exists(INSTAGRAM_AYARLAR_PATH):
        with open(INSTAGRAM_AYARLAR_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

# ---------------------------------------
# --- YAYIN BOTU İÇİN CHROME BAŞLAT VE AI MESAJLAŞMA ---
# ---------------------------------------

def oku_system_prompt():
    if os.path.exists(SYSTEM_PROMPT_PATH):
        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return " ".join(data.get("lines", []))
    return ("You are an AI participant in a live streaming chat (such as on Kick or Twitch). "
            "The streamer's name is Borsaiti. The stream is about stock market and general conversation topics. "
            "Your behavior: Always answer briefly, naturally, and like a real human. "
            "Sometimes make jokes, sometimes be serious. "
            "Occasionally refer to the fact that this is a live stream (e.g., 'the stream is going great'). "
            "Sometimes ask a short follow-up question (e.g., 'Which stocks are you watching lately?'). "
            "Use emojis rarely and not excessively. "
            "If you don't fully understand a topic, respond naturally and ask guiding questions. "
            "Do not talk like a robot. Avoid focusing on helping, focus on casual conversation.")

def delay_sure_belirle():
    return random.randint(10, 45)

def chrome_ile_baslat(profile_path, ayarlar, model, prompt_text):
    lock = threading.Lock()
    profile_id = os.path.basename(profile_path)
    options = uc.ChromeOptions()
    options.user_data_dir = profile_path
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0")

    try:
        driver = uc.Chrome(options=options)
    except Exception as e:
        print(f"❌ Chrome error: {e}")
        return

    driver.get(ayarlar["site"])
    print(f"🕒 AI will start in 60 seconds... ({profile_path})")

    def start_ai():
        SAMPLE_RATE = 48000
        RECORD_SEC = 10
        use_file_index = 1
        system_prompt = {"role": "system", "content": prompt_text}
        chat_history = []

        def build_prompt(user_input):
            chat_history.append({"role": "user", "content": user_input})
            return [system_prompt] + chat_history[-5:]

        while True:
            file_current = f"out_{profile_id}_{use_file_index}.wav"
            file_to_delete = f"out_{profile_id}_{(use_file_index % 3) + 1}.wav"

            try:
                with sc.get_microphone(id=str(sc.default_speaker().name), include_loopback=True).recorder(samplerate=SAMPLE_RATE) as mic:
                    data = mic.record(numframes=SAMPLE_RATE * RECORD_SEC)
                    sf.write(file_current, data[:, 0], samplerate=SAMPLE_RATE)
            except Exception as e:
                print(f"🎙️ Recording error: {e}")
                continue

            try:
                if os.path.exists(file_to_delete):
                    os.remove(file_to_delete)
            except Exception as e:
                print(f"🗑️ Delete error: {e}")

            try:
                recognizer = sr.Recognizer()
                with sr.AudioFile(file_current) as source:
                    audio = recognizer.record(source)
                turkish_text = recognizer.recognize_google(audio, language="tr-TR")
                print(f"🧑 ({profile_id}):", turkish_text)
            except Exception as e:
                print(f"❌ Recognition error ({profile_id}): {e}")
                use_file_index = (use_file_index % 3) + 1
                continue

            translated_text = translate(turkish_text, "en", "tr")
            prompt = build_prompt(translated_text)

            try:
                with lock:
                    response = ollama.chat(model=model, messages=prompt)
                    english_reply = response["message"]["content"].strip().split(".")[0].strip() + "."
                    translated_reply = translate(english_reply, "tr", "en")
            except Exception as e:
                print(f"❌ AI response error ({profile_id}): {e}")
                continue

            delay = delay_sure_belirle()
            print(f"⌛ Reply in {delay} sec... ({profile_id})")
            time.sleep(delay)
            print(f"🤖 ({profile_id}):", translated_reply)
            chat_history.append({"role": "assistant", "content": english_reply})

            try:
                chat_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, ayarlar["input_xpath"]))
                )
                with lock:
                    chat_input.click()
                    chat_input.send_keys(translated_reply)
                    send_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, ayarlar["buton_xpath"]))
                    )
                    send_button.click()
                    print(f"📤 Sent! ({profile_id})")
            except Exception as msg_err:
                print(f"❗ Send error ({profile_id}): {msg_err}")

            use_file_index = (use_file_index % 3) + 1

    threading.Thread(target=lambda: (time.sleep(60), start_ai())).start()

# ---------------------------------------
# --- ANA MENÜ VE KULLANICI SEÇİMLERİ ---
# ---------------------------------------

API_KEY = "cogmito-374giayfaud738q"  # ✅ TOGMITO’ya özel API key örneği
kullanici_key = None


def set_api(key):
    global kullanici_key
    if key != API_KEY:
        raise ValueError("❌ Invalid API key!")
    kullanici_key = key
    print("✅ API key verified!")


def model_sec():
    print("\n🧠 Select AI Model:")
    print("1 - gemma:2b")
    print("2 - mistral")
    print("3 - llama3")
    secim = input("Your choice (1/2/3): ").strip()
    if secim == "1":
        kaydet_model("gemma:2b")
    elif secim == "2":
        kaydet_model("mistral")
    elif secim == "3":
        kaydet_model("llama3")
    else:
        print("❌ Invalid selection!")


def menu_secim_7():
    profiller = yukle_aktif_threadler()
    if not profiller:
        profiller = ["togmito"]
    for profil in profiller:
        profile_path = os.path.join(os.getcwd(), profil)
        os.makedirs(profile_path, exist_ok=True)
        ayarlar = yukle_ayarlar()
        model = yukle_model()
        prompt_text = oku_system_prompt()
        t = threading.Thread(target=chrome_ile_baslat, args=(profile_path, ayarlar, model, prompt_text))
        aktif_threadler.append(t)
        t.start()
    for t in aktif_threadler:
        t.join()


def menu_secim_8_3():
    instagram_gorev_baslat()


def baslat():
    if kullanici_key != API_KEY:
        raise PermissionError("❌ API not verified!")

    if yukle_model() is None:
        print("⚠️ First launch: AI model not selected.")
        model_sec()

    while True:
        print("\n📋 Menu:")
        print("1 - Continue (Start AI Bot)")
        print("2 - Configure (Site and XPaths)")
        print("3 - Prompt Settings (DISABLED)")
        print("4 - Select AI Model")
        print("5 - System Prompt Settings Info")
        print("6 - Create New Chrome Profile")
        print("7 - Multi Launch AI Profiles")
        print("8 - Instagram Bot Menu")
        print("9 - Telegram Yapılandır (Token Gir)")
        print("10 - Telegram Botu Başlat")

        secim = input("Choose (1-10): ").strip()

        if secim == "1":
            profiller = yukle_aktif_threadler()
            if not profiller:
                profiller = ["togmito"]
            for profil in profiller:
                profile_path = os.path.join(os.getcwd(), profil)
                os.makedirs(profile_path, exist_ok=True)
                ayarlar = yukle_ayarlar()
                model = yukle_model()
                prompt_text = oku_system_prompt()
                t = threading.Thread(target=chrome_ile_baslat, args=(profile_path, ayarlar, model, prompt_text))
                aktif_threadler.append(t)
                t.start()
            for t in aktif_threadler:
                t.join()

        elif secim == "2":
            site = input("🌐 Enter site URL: ").strip()
            xpath_input = input("✏️ Input XPath: ").strip()
            xpath_buton = input("📤 Send button XPath: ").strip()
            kaydet_ayarlar({"site": site, "input_xpath": xpath_input, "buton_xpath": xpath_buton})
            print("✅ Settings saved.")

        elif secim == "3":
            print("⚠️ This option is currently disabled.")

        elif secim == "4":
            model_sec()

        elif secim == "5":
            print("⚙️ If you want, edit system_prompt.json manually.")

        elif secim == "6":
            sayac = yukle_profil_sayaci()
            yeni_profil = f"togmito-{sayac}"
            kaydet_profil_sayaci(sayac + 1)
            profile_path = os.path.join(os.getcwd(), yeni_profil)
            os.makedirs(profile_path, exist_ok=True)
            ayarlar = yukle_ayarlar()
            model = yukle_model()
            prompt_text = oku_system_prompt()
            chrome_ile_baslat(profile_path, ayarlar, model, prompt_text)

        elif secim == "7":
            menu_secim_7()

        elif secim == "8":
            instagram_menu()

        elif secim == "9":
            telegram_token_ayarla()

        elif secim == "10":
            telegram_bot_baslat()
            return  # Menüye geri dönmek için telegram_bot_baslat sonunda tekrar baslat() çağrılır

        else:
            print("❌ Invalid selection! Please choose between 1 and 10.")

# ---------------------------------------
# --- INSTAGRAM OTOMASYONU BAŞLANGICI ---
# ---------------------------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Chrome/113.0.5672.126 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/112.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Firefox/117.0"
]

def instagram_menu():
    while True:
        print("\n📸 Instagram Bot Menu:")
        print("1 - Yeni Instagram Hesabı Ekle")
        print("2 - Yapılandırma Yap (Site ve Görev Seç)")
        print("3 - Görevleri Başlat (Tüm Profiller)")
        print("4 - Profil Düzenle (Seç ve Aç)")
        print("5 - Geri Dön (Ana Menü)")

        secim = input("Seçiminiz (1-5): ").strip()

        if secim == "1":
            instagram_yeni_hesap_ekle()
        elif secim == "2":
            instagram_yapilandirma()
        elif secim == "3":
            instagram_gorev_baslat()
        elif secim == "4":
            instagram_profil_duzenle()
        elif secim == "5":
            break
        else:
            print("❌ Geçersiz seçim!")

def instagram_yeni_hesap_ekle():
    profiller = yukle_instagram_profiller()
    yeni_index = len(profiller) + 1
    yeni_profil = f"instagram-{yeni_index}"
    profile_path = os.path.join(os.getcwd(), yeni_profil)
    os.makedirs(profile_path, exist_ok=True)

    selected_agent = random.choice(USER_AGENTS)

    options = uc.ChromeOptions()
    options.user_data_dir = profile_path
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={selected_agent}")
    options.add_argument("--profile-directory=Default")  # 👈 PROFİL DİZİNİ EKLENDİ
    options.headless = False  # 👈 HEADLESS KAPALI: GİRİŞ KAYDEDİLİR

    try:
        driver = uc.Chrome(options=options)
        driver.get("https://www.instagram.com/")
        print(f"🔓 Yeni Instagram hesabı açıldı: {yeni_profil} (Header: {selected_agent})")
        input("➡️ Giriş yaptıktan sonra tarayıcıyı kapatıp ENTER'a basın...")
        driver.quit()
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

    profiller.append({
        "isim": yeni_profil,
        "user_agent": selected_agent
    })
    kaydet_instagram_profiller(profiller)
    print(f"✅ Instagram profili kaydedildi: {yeni_profil}")

def instagram_yapilandirma():
    site = input("🌐 Gitmek istediğiniz tam Instagram gönderi linki (https:// ile): ").strip()
    print("\n🎯 Hangi görevi yapacaksınız?")
    print("1 - Takip Et Butonuna Bas")
    print("2 - Beğeni Butonuna Bas")
    hedef_secim = input("Seçiminiz (1/2): ").strip()

    if hedef_secim == "1":
        hedef = "takip"
    elif hedef_secim == "2":
        hedef = "begeni"
    else:
        print("❌ Geçersiz seçim!")
        return

    kaydet_instagram_ayarlar({"site": site, "hedef": hedef})
    print("✅ Yapılandırma kaydedildi!")

def instagram_gorev_baslat():
    profiller = yukle_instagram_profiller()
    ayarlar = yukle_instagram_ayarlar()

    if not profiller:
        print("⚠️ Hiç Instagram profili eklenmemiş!")
        return

    if not ayarlar:
        print("⚠️ Yapılandırma yapılmamış!")
        return

    for profil_info in profiller:
        profil = profil_info["isim"]
        user_agent = profil_info["user_agent"]
        profile_path = os.path.join(os.getcwd(), profil)

        options = uc.ChromeOptions()
        options.user_data_dir = profile_path
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"user-agent={user_agent}")
        options.add_argument("--profile-directory=Default")  # 👈 PROFİL DİZİNİ EKLENDİ
        options.headless = False  # 👈 HEADLESS KAPALI: GİRİŞLER KAYDEDİLİR

        try:
            print(f"🚀 {profil} profili başlatılıyor...")
            driver = uc.Chrome(options=options)
            driver.get(ayarlar["site"])
            print("⌛ Sayfa yükleniyor...")
            time.sleep(10)

            hedef = ayarlar.get("hedef", "")
            buton_bulundu = False

            if hedef == "takip":
                buttons = driver.find_elements(By.TAG_NAME, "button")
                for button in buttons:
                    if "takip" in button.text.lower():
                        button.click()
                        buton_bulundu = True
                        print(f"✅ Takip Et'e basıldı! ({profil})")
                        time.sleep(5)
                        break

            elif hedef == "begeni":
                try:
                    like_icon = driver.find_element(By.XPATH, "//*[name()='svg' and (@aria-label='Beğen' or @aria-label='Like')]")
                    like_button = like_icon.find_element(By.XPATH, "./ancestor::button")
                    like_button.click()
                    buton_bulundu = True
                    print(f"❤️ Beğeni yapıldı! ({profil})")
                    time.sleep(5)
                except Exception as e:
                    print(f"❌ Beğeni tıklama hatası ({profil}): {e}")

            if not buton_bulundu:
                print(f"⚠️ {profil} için buton bulunamadı!")

            driver.quit()

        except Exception as e:
            print(f"❌ Hata ({profil}): {e}")

    print("🎯 Tüm görevler tamamlandı!")

def instagram_profil_duzenle():
    profiller = yukle_instagram_profiller()
    if not profiller:
        print("⚠️ Hiç Instagram profili eklenmemiş!")
        return

    print("🔢 Mevcut Profiller:")
    for idx, profil_info in enumerate(profiller):
        print(f"{idx + 1} - {profil_info['isim']}")

    secim = input("Düzenlemek istediğiniz profilin numarası: ").strip()
    if not secim.isdigit() or int(secim) < 1 or int(secim) > len(profiller):
        print("❌ Geçersiz seçim!")
        return

    profil_secimi = profiller[int(secim) - 1]["isim"]
    user_agent = profiller[int(secim) - 1]["user_agent"]
    profile_path = os.path.join(os.getcwd(), profil_secimi)

    options = uc.ChromeOptions()
    options.user_data_dir = profile_path
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--profile-directory=Default")  # 👈 PROFİL DİZİNİ EKLENDİ
    options.headless = False  # 👈 HEADLESS KAPALI: GİRİŞ EKRANI GÖRÜNÜR

    try:
        driver = uc.Chrome(options=options)
        driver.get("https://www.instagram.com/")
        print(f"🛠️ {profil_secimi} profili açıldı.")
        input("🔒 Giriş yaptıktan sonra ENTER'a basın...")
        driver.quit()
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

# ---------------------------------------
# --- INSTAGRAM OTOMASYONU BİTİŞİ ---
# ---------------------------------------

# ---------------------------------------
# --- TELEGRAM KONTROLLÜ OTOMASYON SİSTEMİ ---
# ---------------------------------------

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import json
import os
import asyncio
import nest_asyncio
import threading

TELEGRAM_CONFIG_PATH = "telegram_config.json"
AKTIF_TELEGRAM_ID = set()
GECICI_KULLANICILAR = {}  # user_id -> "beklenen_kod"
BOT_SIFRESI = "1234"

menu_butonu = ReplyKeyboardMarkup(
    [["Kick İşlemini Başlat"],
     ["Kick Yapılandır"],
     ["Instagram İşlemini Başlat"],
     ["Instagram Yapılandır"]],
    resize_keyboard=True
)

def kaydet_telegram_token(token):
    with open(TELEGRAM_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"token": token}, f)

def yukle_telegram_token():
    if os.path.exists(TELEGRAM_CONFIG_PATH):
        with open(TELEGRAM_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("token", None)
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in AKTIF_TELEGRAM_ID:
        await update.message.reply_text("✅ Zaten giriş yaptın.", reply_markup=menu_butonu)
    else:
        GECICI_KULLANICILAR[user_id] = "sifre"
        await update.message.reply_text("🔐 Giriş için şifreyi giriniz:")

async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id in AKTIF_TELEGRAM_ID:
        if text == "Kick İşlemini Başlat":
            await update.message.reply_text("🌐 Kick işlemi başlatılıyor...")
            threading.Thread(target=menu_secim_7).start()
        elif text == "Kick Yapılandır":
            await update.message.reply_text("🔧 Kick yapılandırması (şimdilik desteklenmiyor)...")
        elif text == "Instagram İşlemini Başlat":
            await update.message.reply_text("🤝 Instagram görevi başlatılıyor...")
            threading.Thread(target=menu_secim_8_3).start()
        elif text == "Instagram Yapılandır":
            await update.message.reply_text("📎 Profil linkini gönderin:")
            GECICI_KULLANICILAR[user_id] = "ig_link"
        elif GECICI_KULLANICILAR.get(user_id) == "ig_eylem":
            if text.lower() in ["takip", "beğeni"]:
                with open("instagram_ayarlar.json", "w", encoding="utf-8") as f:
                    json.dump({"eylem": text.lower()}, f)
                del GECICI_KULLANICILAR[user_id]
                await update.message.reply_text("✅ Instagram yapılandırması tamamlandı!", reply_markup=menu_butonu)
            else:
                await update.message.reply_text("⚠️ Sadece 'takip' veya 'beğeni' yazabilirsiniz.")
        elif GECICI_KULLANICILAR.get(user_id) == "ig_link":
            with open("instagram_ayarlar.json", "w", encoding="utf-8") as f:
                json.dump({"link": text}, f)
            GECICI_KULLANICILAR[user_id] = "ig_eylem"
            await update.message.reply_text("📌 Şimdi 'takip' mi 'beğeni' mi yapmak istediğinizi yazın:")
        else:
            await update.message.reply_text("❌ Geçersiz komut.")
    elif user_id in GECICI_KULLANICILAR:
        if text == BOT_SIFRESI:
            AKTIF_TELEGRAM_ID.add(user_id)
            del GECICI_KULLANICILAR[user_id]
            await update.message.reply_text("✅ Giriş başarılı!", reply_markup=menu_butonu)
        else:
            await update.message.reply_text("❌ Hatalı şifre!")
    else:
        await update.message.reply_text("ℹ️ Lütfen /start komutunu kullan.")

def telegram_bot_baslat():
    token = yukle_telegram_token()
    if not token:
        print("❌ Telegram tokenı ayarlanmamış.")
        return

    async def main():
        app = ApplicationBuilder().token(token).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_handler))
        print("🚀 Telegram bot çalışıyor...")
        await app.run_polling()

    try:
        nest_asyncio.apply()
        threading.Thread(target=lambda: asyncio.run(main())).start()
    except Exception as e:
        print(f"❌ Bot başlatma hatası: {e}")

    # Konsolu bloklamasın diye ana menüyü tekrar çağır
    try:
        from main import baslat
        threading.Thread(target=baslat).start()
    except:
        print("ℹ️ Ana menüye dönülemiyor. main.py'de 'baslat' fonksiyonu olmalı.")

def telegram_token_ayarla():
    token = input("📡 Telegram Bot Token'ınızı girin: ").strip()
    kaydet_telegram_token(token)
    print("✅ Telegram bot token kaydedildi.")

def menu_secim_7():
    print("Kick görevleri başlatılıyor...")
    # Gerçek görev fonksiyonunuzu buraya ekleyin

def menu_secim_8_3():
    print("Instagram görevleri başlatılıyor...")
    # Gerçek görev fonksiyonunuzu buraya ekleyin

# ---------------------------------------
# --- ANA ÇALIŞTIRICI ---
# ---------------------------------------

if __name__ == "__main__":
    print("🚀 Bot sistemi başlatılıyor...")
    print("✅ API doğrulaması yapılıyor...")
    try:
        kullanici_api = input("🔑 API Key giriniz: ").strip()
        set_api(kullanici_api)
        baslat()
    except Exception as e:
        print(f"❌ Başlangıçta hata oluştu: {e}")
