from fastapi import FastAPI, Request
from servicios.openai_agent import generar_respuesta_ia

# ESTA ES LA LÍNEA QUE FALTABA Y QUE UVICORN ESTABA BUSCANDO
app = FastAPI()

# 1. MEMORIA EN VIVO (Mantiene el contexto por usuario)
memoria_charlas = {}

@app.post("/webhook")
async def recibir_mensaje(datos: Request):
    cuerpo = await datos.json()
    
    # Extraemos solo lo necesario para el flujo de texto
    texto_usuario = str(cuerpo.get("texto", "")).strip()
    identificador = str(cuerpo.get("user_id", "usuario_default")).strip()

    print(f"📥 MENSAJE RECIBIDO de [{identificador}]: '{texto_usuario[:45]}...'")

    # Validación básica de seguridad
    if not texto_usuario or texto_usuario == "Última entrada de texto":
        return {"respuesta_servidor": "Hola, ¿en qué te puedo ayudar hoy? Si tienes alguna pregunta sobre tratamientos estéticos o deseas agendar una valoración, estoy aquí para apoyarte."}

    # BOTÓN DE REINICIO DE MEMORIA
    palabras_reinicio = ["reiniciar", "borrar", "empezar de cero", "clear", "nueva consulta"]
    if any(palabra in texto_usuario.lower() for palabra in palabras_reinicio):
        memoria_charlas[identificador] = []
        return {"respuesta_servidor": "¡Listo! He borrado el historial de nuestra conversación anterior. ¿En qué nuevo tratamiento o servicio te gustaría que te ayude hoy?"}

    # 2. GESTIÓN DE MEMORIA (Historial de 8 mensajes)
    if identificador not in memoria_charlas:
        memoria_charlas[identificador] = []

    memoria_charlas[identificador].append({"role": "user", "content": texto_usuario})

    if len(memoria_charlas[identificador]) > 8:
        memoria_charlas[identificador] = memoria_charlas[identificador][-8:]

    print(f"--- Memoria actual del usuario [{identificador}] (Mensajes: {len(memoria_charlas[identificador])}) ---")

    # 3. PROCESAMIENTO CON LA IA
    respuesta_ia = await generar_respuesta_ia(memoria_charlas[identificador])

    # 4. GUARDAMOS RESPUESTA DE LA IA
    memoria_charlas[identificador].append({"role": "assistant", "content": respuesta_ia})

    print("=== IA RESPONDE ===", respuesta_ia)

    return {"respuesta_servidor": respuesta_ia}