import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Obtiene el token desde las variables de entorno de Render
TOKEN = os.getenv("TELEGRAM_TOKEN")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Verifica si el mensaje contiene un enlace de TikTok
    if "tiktok.com" in text or "vm.tiktok.com" in text:
        await update.message.reply_text("⏳ Procesando enlace de TikTok...")
        try:
            # Petición a la API gratuita de TikWM para obtener el video sin marca de agua
            api_url = f"https://www.tikwm.com/api/?url={text}"
            response = requests.get(api_url).json()
            
            if response.get("code") == 0:
                # Extrae el enlace directo del video y el título
                video_url = response["data"]["play"]
                title = response["data"].get("title", "TikTok sin marca de agua")
                
                # Envía el video directamente a Telegram usando la URL (Cero almacenamiento local)
                await update.message.reply_video(video=video_url, caption=title)
            else:
                await update.message.reply_text("❌ No pude obtener el video. Asegúrate de que el enlace sea público y válido.")
        except Exception as e:
            await update.message.reply_text("⚠️ Ocurrió un error inesperado al conectar con el servicio.")
    else:
        await update.message.reply_text("👋 ¡Hola! Envíame un enlace de TikTok y te lo descargo sin marca de agua.")

def main():
    if not TOKEN:
        print("Error: TELEGRAM_TOKEN no está configurado.")
        return

    # Construye la aplicación del bot
    application = ApplicationBuilder().token(TOKEN).build()

    # Manejador para los mensajes de texto
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # Inicia el bot
    print("El bot de TikTok está corriendo...")
    application.run_polling()

if __name__ == "__main__":
    main()
