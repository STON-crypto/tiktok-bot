import os
import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Obtener el token directamente de las variables de entorno de la nube (Koyeb)
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Función para extraer y limpiar el enlace de TikTok (ya sea directo o de tipo vm.tiktok.com)
def extract_tiktok_url(text: str) -> str:
    # Patrón RegEx robusto para encontrar URLs de TikTok en cualquier texto
    url_pattern = r'https?://(?:m|www|vm|vt)?\.?tiktok\.com/[^\s]+'
    match = re.search(url_pattern, text)
    if match:
        raw_url = match.group(0)
        # Si es un enlace corto, devolvemos tal cual para que la API lo resuelva
        if "vm.tiktok.com" in raw_url or "vt.tiktok.com" in raw_url:
            return raw_url
        # Si es un enlace largo, limpiamos los parámetros de rastreo (lo que viene después del signo ?)
        clean_url = raw_url.split('?')[0]
        return clean_url
    return None

# Manejador principal cuando el usuario envía un mensaje con un enlace de TikTok
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    tiktok_url = extract_tiktok_url(text)

    if not tiktok_url:
        # Si no manda un enlace válido, no hacemos nada o podemos ignorarlo
        return

    # Enviamos un mensaje de aviso mientras procesamos la descarga en streaming
    processing_msg = await update.message.reply_text("🔄 Procesando video sin marca de agua...")

    try:
        # Consultamos a la API pública de tikwm para obtener el video en streaming directo
        api_url = f"https://www.tikwm.com/api/?url={tiktok_url}"
        response = requests.get(api_url)
        data = response.json()

        if data.get("code") == 0:
            # Obtenemos la URL directa del video libre de marca de agua
            video_url = data["data"]["play"]
            author = data["data"]["author"]["nickname"]
            title = data["data"]["title"]

            caption = f"🎬 **{title}**\n👤 Autor: {author}\n🤖 *Descargado por tu Bot 24/7*"

            # Enviamos el video a Telegram usando el enlace directo (arquitectura zero-storage, sin gastar disco)
            await update.message.reply_video(
                video=video_url,
                caption=caption,
                parse_mode="Markdown"
            )
            # Borramos el mensaje de "procesando" para dejar el chat limpio
            await processing_msg.delete()
        else:
            await processing_msg.edit_text("❌ Error: No se pudo extraer el video. Intenta con otro enlace.")
            
    except Exception as e:
        await processing_msg.edit_text(f"❌ Ocurrió un error inesperado al procesar el video.")

def main():
    if not TOKEN:
        print("Error: No se encontró la variable de entorno TELEGRAM_TOKEN.")
        return

    # Inicializamos el bot con la versión moderna de python-telegram-bot
    app = ApplicationBuilder().token(TOKEN).build()

    # Filtramos cualquier mensaje de texto que contenga un enlace de TikTok
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 Bot iniciado y listo para operar en la nube...")
    app.run_polling()

if __name__ == "__main__":
    main()
