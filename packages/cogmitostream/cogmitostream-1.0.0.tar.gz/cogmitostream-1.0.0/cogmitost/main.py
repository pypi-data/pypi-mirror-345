# AI destekli stream viewer'a özel sadeleştirilmiş versiyon

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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import speech_recognition as sr

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

SETTINGS_PATH = "data.json"
MODEL_PATH = "model.json"
SYSTEM_PROMPT_PATH = "system_prompt.json"
PROFILS_PATH = "profils.json"
AKTIF_PATH = "aktif_profiller.json"
aktif_threadler = []

# --- VERİ YÜKLE/KAYDET ---

def kaydet_aktif_threadler(liste):
    with open(AKTIF_PATH, "w", encoding="utf-8") as f:
        json.dump({"aktif": liste}, f)

def yukle_aktif_threadler():
    if os.path.exists(AKTIF_PATH):
        with open(AKTIF_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("aktif", [])
    return []

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

def oku_system_prompt():
    if os.path.exists(SYSTEM_PROMPT_PATH):
        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return " ".join(data.get("lines", []))
    return "You are an AI in a live stream. Talk like a real human."

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
                continue

            try:
                if os.path.exists(file_to_delete):
                    os.remove(file_to_delete)
            except: pass

            try:
                recognizer = sr.Recognizer()
                with sr.AudioFile(file_current) as source:
                    audio = recognizer.record(source)
                turkish_text = recognizer.recognize_google(audio, language="tr-TR")
                print(f"🧑 ({profile_id}):", turkish_text)
            except:
                use_file_index = (use_file_index % 3) + 1
                continue

            translated_text = translate(turkish_text, "en", "tr")
            prompt = build_prompt(translated_text)

            try:
                with lock:
                    response = ollama.chat(model=model, messages=prompt)
                    english_reply = response["message"]["content"].strip().split(".")[0].strip() + "."
                    translated_reply = translate(english_reply, "tr", "en")
            except:
                continue

            delay = delay_sure_belirle()
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
            except: pass

            use_file_index = (use_file_index % 3) + 1

    threading.Thread(target=lambda: (time.sleep(60), start_ai())).start()

def menu_secim_7():
    profiller = yukle_aktif_threadler()
    if not profiller:
        profiller = ["viewer1"]
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

def yukle_ayarlar():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def baslat():
    if yukle_model() is None:
        print("⚠️ Model seçilmedi. Lütfen model belirleyin.")
        model_sec()

    while True:
        print("\n📋 Menü:")
        print("1 - AI Bot Başlat")
        print("2 - Ayarları Yapılandır")
        print("3 - Model Seç")

        secim = input("Seçiminiz (1-3): ").strip()
        if secim == "1":
            menu_secim_7()
        elif secim == "2":
            site = input("Site URL: ")
            input_xpath = input("Input XPath: ")
            buton_xpath = input("Gönder Butonu XPath: ")
            kaydet_ayarlar({"site": site, "input_xpath": input_xpath, "buton_xpath": buton_xpath})
        elif secim == "3":
            model_sec()
        else:
            print("❌ Geçersiz seçim!")

def kaydet_ayarlar(data):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)

def model_sec():
    print("Mevcut Modeller:")
    print("1 - gemma:2b")
    print("2 - mistral")
    print("3 - llama3")
    secim = input("Seçiminiz (1-3): ").strip()
    if secim == "1":
        kaydet_model("gemma:2b")
    elif secim == "2":
        kaydet_model("mistral")
    elif secim == "3":
        kaydet_model("llama3")
    else:
        print("Geçersiz model.")

if __name__ == "__main__":
    print("🚀 Cogmito AI Stream Viewer Başlatılıyor...")
    baslat()
