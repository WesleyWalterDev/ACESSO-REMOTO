"""
agente_controle.py
Desenvolvido por Wesley Walter

Roda na máquina do cliente. Fica escutando em ws://localhost:8765 e espera
o usuario.html (aberto no navegador) conectar. Os comandos de mouse/teclado
que chegam do suporte passam pelo WebRTC, caem aqui e são executados de
verdade na máquina com pyautogui.

Uso:
    python3 agente_controle.py

Deixa o terminal aberto durante o atendimento. Ctrl+C encerra.
"""

import asyncio
import json
import sys

import pyautogui
import websockets

pyautogui.FAILSAFE = False  # não quero que trave se o mouse for pro canto
pyautogui.PAUSE = 0  # sem delay entre os comandos

# no Mac a tecla "de comando" chama "command" no pyautogui, no Windows é "win"
NOME_TECLA_META = "command" if sys.platform == "darwin" else "win"

MAPA_TECLAS = {
    "Enter": "enter", "Backspace": "backspace", "Tab": "tab", "Escape": "esc",
    "ArrowUp": "up", "ArrowDown": "down", "ArrowLeft": "left", "ArrowRight": "right",
    "Delete": "delete", " ": "space", "Home": "home", "End": "end",
    "PageUp": "pageup", "PageDown": "pagedown", "CapsLock": "capslock",
    "Meta": NOME_TECLA_META,
}


def tecla_pyautogui(tecla_js: str) -> str:
    if tecla_js in MAPA_TECLAS:
        return MAPA_TECLAS[tecla_js]
    if len(tecla_js) == 1:
        return tecla_js
    return tecla_js.lower()


def executar_comando(cmd: dict):
    acao = cmd.get("acao")

    if acao == "mover":
        pyautogui.moveTo(cmd["x"], cmd["y"], _pause=False)

    elif acao == "clique":
        botao = "right" if cmd.get("botao") == "direito" else "left"
        pyautogui.moveTo(cmd["x"], cmd["y"], _pause=False)
        pyautogui.click(button=botao)

    elif acao == "duplo_clique":
        pyautogui.moveTo(cmd["x"], cmd["y"], _pause=False)
        pyautogui.doubleClick()

    elif acao == "scroll":
        pyautogui.scroll(int(cmd.get("dy", 0) * -1))

    elif acao == "tecla":
        tecla = tecla_pyautogui(cmd["tecla"])
        modificadores = []
        if cmd.get("ctrl"):
            modificadores.append("ctrl")
        if cmd.get("alt"):
            modificadores.append("alt")
        if cmd.get("meta"):
            modificadores.append(NOME_TECLA_META)
        if cmd.get("shift") and len(tecla) > 1:
            modificadores.append("shift")
        if modificadores:
            pyautogui.hotkey(*modificadores, tecla)
        else:
            pyautogui.press(tecla)

    elif acao == "atalho":
        # botões prontos tipo "Win+D", "Alt+Tab" que o painel de suporte manda
        teclas = [tecla_pyautogui(t) for t in cmd.get("teclas", [])]
        if len(teclas) == 1:
            pyautogui.press(teclas[0])
        elif len(teclas) > 1:
            pyautogui.hotkey(*teclas)

    elif acao == "texto":
        pyautogui.write(cmd["texto"], interval=0.01)


async def tratar_conexao(websocket):
    print("[+] Navegador conectado ao agente.")
    try:
        async for mensagem in websocket:
            try:
                cmd = json.loads(mensagem)
                executar_comando(cmd)
            except Exception as e:
                print("[!] Erro ao executar comando:", e)
    except websockets.exceptions.ConnectionClosed:
        pass
    print("[-] Navegador desconectado.")


async def main():
    largura, altura = pyautogui.size()
    print(f"[*] Resolução desta máquina: {largura}x{altura}")
    print("[*] Escutando em ws://localhost:8765")
    print("[*] Deixa aberto e abre o usuario.html no navegador.")
    async with websockets.serve(tratar_conexao, "localhost", 8765):
        await asyncio.Future()  # fica rodando até fechar


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] Agente encerrado.")
