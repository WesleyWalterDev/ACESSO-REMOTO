"""
iniciar_atendimento.py
Desenvolvido por Wesley Walter

Programa único pra rodar na máquina do cliente. Dois cliques (ou
"python3 iniciar_atendimento.py") e ele já:
  1) sobe o agente de controle remoto (mouse/teclado)
  2) abre a página de atendimento no navegador
  3) mostra uma janelinha de status com botão de encerrar

Não precisa mexer em mais nada. Pra terminar, fecha a janelinha ou clica
em "Encerrar atendimento".
"""

import asyncio
import json
import os
import sys
import tempfile
import threading
import webbrowser
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

try:
    import pyautogui
    import websockets
except ImportError:
    print("Faltam dependências. Roda antes:")
    print("    pip install -r requirements_agente.txt")
    sys.exit(1)

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0

# no Mac a tecla "de comando" chama "command" no pyautogui, no Windows é "win"
NOME_TECLA_META = "command" if sys.platform == "darwin" else "win"

# HTML da página de atendimento (embutido aqui, não precisa de outro arquivo)
PAGINA_HTML = r"""<!--
  Atendimento remoto - painel do cliente
  Desenvolvido por Wesley Walter
-->
<!doctype html>
<html lang="pt-br">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atendimento — área do cliente</title>
<script src="https://unpkg.com/peerjs@1.5.4/dist/peerjs.min.js"></script>
<style>
  :root {
    --bg: #0b0f0e; --bg-panel: #121816; --bg-raised: #182220; --line: #23302c;
    --text: #e7efec; --text-dim: #8ea39a;
    --accent: #3ddc97; --accent-dim: #1f6e4d; --warn: #e0a458; --danger: #e0685b;
    --mono: 'SF Mono', 'JetBrains Mono', ui-monospace, Consolas, monospace;
    --sans: 'Inter', system-ui, -apple-system, sans-serif;
  }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--text); font-family:var(--sans); min-height:100vh; }
  .topo { display:flex; align-items:center; justify-content:space-between; padding:18px 28px; border-bottom:1px solid var(--line); }
  .marca { display:flex; align-items:center; gap:10px; }
  .marca .ponto { width:10px; height:10px; border-radius:50%; background:var(--text-dim); }
  .marca .ponto.on { background:var(--accent); box-shadow:0 0 8px var(--accent); }
  .marca span { font-weight:600; letter-spacing:0.02em; }
  .status-txt { font-family:var(--mono); font-size:12px; color:var(--text-dim); }
  main { max-width:640px; margin:0 auto; padding:40px 24px 80px; }
  .cartao { background:var(--bg-panel); border:1px solid var(--line); border-radius:10px; padding:28px; margin-bottom:20px; }
  .cartao h2 { margin:0 0 6px; font-size:15px; text-transform:uppercase; letter-spacing:0.08em; color:var(--text-dim); font-weight:600; }
  .cartao p.legenda { margin:0 0 18px; color:var(--text-dim); font-size:14px; line-height:1.5; }
  .codigo-central { text-align:center; padding: 16px 0; }
  .codigo { font-family:var(--mono); font-size:44px; letter-spacing:0.2em; color:var(--accent); font-weight:700; }
  .codigo-legenda { color:var(--text-dim); font-size:13px; margin-top:8px; }
  button {
    font-family:var(--sans); font-weight:600; font-size:15px; border:none; border-radius:8px;
    padding:14px 20px; cursor:pointer; background:var(--accent); color:#072016;
    transition: transform .08s ease, opacity .15s ease; width:100%;
  }
  button:hover { opacity:0.9; } button:active { transform:scale(0.98); }
  button.secundario { background:var(--bg-raised); color:var(--text); border:1px solid var(--line); }
  button:disabled { opacity:0.35; cursor:not-allowed; }
  .aviso-conexao {
    display:flex; align-items:center; gap:10px; background: rgba(61,220,151,0.08);
    border:1px solid var(--accent-dim); border-radius:8px; padding:12px 16px; margin-bottom:16px;
    font-size:14px; color: var(--accent); display:none;
  }
  .aviso-conexao.visivel { display:flex; }
  .drop {
    margin-top:14px; border:2px dashed var(--line); border-radius:8px; padding:24px;
    text-align:center; color:var(--text-dim); cursor:pointer; font-size:14px;
  }
  .drop.arraste-sobre { border-color:var(--accent); color:var(--accent); background:rgba(61,220,151,0.05); }
  .lista-arquivos { list-style:none; padding:0; margin:14px 0 0; }
  .lista-arquivos li { display:flex; justify-content:space-between; align-items:center; padding:10px 12px; background:var(--bg-raised); border-radius:6px; margin-bottom:8px; font-size:14px; }
  .lista-arquivos .barra { height:4px; background:var(--line); border-radius:3px; overflow:hidden; flex:1; margin:0 12px; }
  .lista-arquivos .barra > div { height:100%; background:var(--accent); width:0%; transition:width .2s; }
  .lista-arquivos a { color:var(--accent); text-decoration:none; font-weight:600; }
  .rodape-nota { font-size:12px; color:var(--text-dim); margin-top:24px; line-height:1.6; text-align:center; }
  .linha-agente { display:flex; align-items:center; gap:10px; }
  .ponto-agente { width:9px; height:9px; border-radius:50%; background:var(--danger); flex-shrink:0; }
  .ponto-agente.on { background:var(--accent); box-shadow:0 0 8px var(--accent); }
  .modal-sobre {
    display:none; position:fixed; inset:0; background:rgba(0,0,0,0.6);
    align-items:center; justify-content:center; z-index:100;
  }
  .modal-sobre.aberto { display:flex; }
  .modal-sobre-caixa {
    background:var(--bg-panel); border:1px solid var(--line); border-radius:10px;
    padding:28px; max-width:320px; text-align:center;
  }
  .modal-sobre-caixa h3 { margin:0 0 10px; }
  .modal-sobre-caixa p { color:var(--text-dim); margin:0 0 20px; }
</style>
</head>
<body>

<div class="topo">
  <div class="marca"><div class="ponto" id="ponto-status"></div><span>Atendimento</span></div>
  <div style="display:flex; align-items:center; gap:16px;">
    <div class="status-txt" id="texto-status">gerando código…</div>
    <a href="#" onclick="abrirSobre(); return false;" style="font-size:12px; color:var(--text-dim); text-decoration:underline;">Sobre</a>
  </div>
</div>

<div class="modal-sobre" id="modal-sobre" onclick="if(event.target===this) fecharSobre()">
  <div class="modal-sobre-caixa">
    <h3>Atendimento remoto</h3>
    <p>Desenvolvido por <strong>Wesley Walter</strong>.</p>
    <button class="secundario" onclick="fecharSobre()">Fechar</button>
  </div>
</div>

<main>

  <div class="cartao">
    <h2>Seu código de atendimento</h2>
    <p class="legenda">Informe este código para a pessoa do suporte técnico. Assim que ela conectar, você poderá compartilhar sua tela.</p>
    <div class="codigo-central">
      <div class="codigo" id="meu-codigo">------</div>
      <div class="codigo-legenda">aguardando o suporte se conectar…</div>
    </div>
  </div>

  <div class="cartao">
    <div class="aviso-conexao" id="aviso-conectado">✓ Suporte conectado</div>
    <h2>Compartilhar tela</h2>
    <p class="legenda">Clique abaixo quando estiver pronto. O navegador vai perguntar qual tela ou janela você quer mostrar.</p>
    <button id="btn-compartilhar" onclick="compartilharTela()" disabled>Iniciar compartilhamento de tela</button>
    <button id="btn-parar-tela" class="secundario" style="margin-top:10px; display:none;" onclick="pararCompartilhamento()">Parar compartilhamento</button>
  </div>

  <div class="cartao">
    <h2>Controle remoto</h2>
    <p class="legenda">
      Para o suporte poder mexer no mouse e teclado (não só ver a tela), abra o
      programa <strong>agente_controle.py</strong> nesta máquina e deixe rodando.
    </p>
    <div class="linha-agente">
      <div class="ponto-agente" id="ponto-agente"></div>
      <span id="texto-agente" style="font-size:14px; color:var(--text-dim);">agente não conectado</span>
    </div>
  </div>

  <div class="cartao">
    <h2>Arquivos</h2>
    <p class="legenda">Envie um arquivo para o suporte, ou receba arquivos que o suporte enviar para você.</p>
    <div class="drop" id="area-drop" onclick="document.getElementById('input-arquivo').click()">
      Clique aqui ou arraste um arquivo para enviar ao suporte
    </div>
    <input type="file" id="input-arquivo" style="display:none" onchange="enviarArquivoSelecionado(event)">
    <ul class="lista-arquivos" id="lista-arquivos"></ul>
  </div>

  <div class="rodape-nota">
    Esta página compartilha apenas sua tela e arquivos que você escolher enviar.<br>
    Nenhum comando é executado no seu computador.
  </div>

</main>

<script>
function abrirSobre() { document.getElementById('modal-sobre').classList.add('aberto'); }
function fecharSobre() { document.getElementById('modal-sobre').classList.remove('aberto'); }

let peer = null;
let conexaoDados = null;
let chamadaAtiva = null;
let streamLocal = null;

const elMeuCodigo = document.getElementById('meu-codigo');
const elStatus = document.getElementById('texto-status');
const elPonto = document.getElementById('ponto-status');
const elAvisoConectado = document.getElementById('aviso-conectado');
const elBtnCompartilhar = document.getElementById('btn-compartilhar');
const elBtnPararTela = document.getElementById('btn-parar-tela');
const listaArquivos = document.getElementById('lista-arquivos');
const elPontoAgente = document.getElementById('ponto-agente');
const elTextoAgente = document.getElementById('texto-agente');

let wsAgente = null;

function conectarAgenteLocal() {
  try {
    wsAgente = new WebSocket('ws://localhost:8765');
    wsAgente.onopen = () => {
      elPontoAgente.classList.add('on');
      elTextoAgente.textContent = 'agente conectado — controle remoto disponível';
      notificarStatusAgente(true);
    };
    wsAgente.onclose = () => {
      elPontoAgente.classList.remove('on');
      elTextoAgente.textContent = 'agente não conectado — rode o agente_controle.py';
      wsAgente = null;
      notificarStatusAgente(false);
      setTimeout(conectarAgenteLocal, 3000);
    };
    wsAgente.onerror = () => {};
  } catch (e) {
    setTimeout(conectarAgenteLocal, 3000);
  }
}
conectarAgenteLocal();

function notificarStatusAgente(conectado) {
  if (conexaoDados && conexaoDados.open) {
    conexaoDados.send({ tipo: 'agente-status', conectado });
  }
}

function gerarCodigo() {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let c = '';
  for (let i = 0; i < 6; i++) c += chars[Math.floor(Math.random() * chars.length)];
  return c;
}

function atualizarStatus(texto, conectado) {
  elStatus.textContent = texto;
  elPonto.classList.toggle('on', !!conectado);
}

function iniciarPeer() {
  const meuCodigo = gerarCodigo();
  peer = new Peer(meuCodigo);

  peer.on('open', (id) => {
    elMeuCodigo.textContent = id;
    atualizarStatus('aguardando suporte…', false);
  });

  peer.on('connection', (conn) => {
    // o suporte abre dois canais: um confiável (cliques, teclas, arquivos)
    // e um rápido sem garantia de entrega, só pra posição do mouse (evita fila/delay)
    if (conn.label === 'rapido') {
      conn.on('data', (dado) => tratarDadoRecebido(dado));
      return;
    }
    conexaoDados = conn;
    conn.on('open', () => {
      atualizarStatus('suporte conectado', true);
      elAvisoConectado.classList.add('visivel');
      elBtnCompartilhar.disabled = false;
      notificarStatusAgente(wsAgente !== null && wsAgente.readyState === WebSocket.OPEN);
    });
    conn.on('data', (dado) => tratarDadoRecebido(dado));
    conn.on('close', () => {
      atualizarStatus('suporte desconectado', false);
      elAvisoConectado.classList.remove('visivel');
      elBtnCompartilhar.disabled = true;
    });
  });

  peer.on('error', (err) => {
    console.error(err);
    atualizarStatus('erro: ' + err.type, false);
  });
}

async function compartilharTela() {
  try {
    streamLocal = await navigator.mediaDevices.getDisplayMedia({ video: true });
  } catch (e) {
    alert('Não foi possível iniciar o compartilhamento: ' + e.message);
    return;
  }
  if (!conexaoDados) { alert('Aguarde o suporte se conectar primeiro.'); return; }
  chamadaAtiva = peer.call(conexaoDados.peer, streamLocal);
  elBtnCompartilhar.style.display = 'none';
  elBtnPararTela.style.display = 'block';

  const config = streamLocal.getVideoTracks()[0].getSettings();
  conexaoDados.send({ tipo: 'resolucao-tela', width: config.width, height: config.height });

  streamLocal.getVideoTracks()[0].addEventListener('ended', pararCompartilhamento);
}

function pararCompartilhamento() {
  if (streamLocal) { streamLocal.getTracks().forEach(t => t.stop()); streamLocal = null; }
  if (chamadaAtiva) { chamadaAtiva.close(); chamadaAtiva = null; }
  elBtnCompartilhar.style.display = 'block';
  elBtnPararTela.style.display = 'none';
}

// --- Transferência de arquivos ---

const TAMANHO_PEDACO = 16 * 1024;
const recebendo = {};

function enviarArquivoSelecionado(evento) {
  const arquivo = evento.target.files[0];
  if (arquivo) enviarArquivo(arquivo);
  evento.target.value = '';
}

const areaDrop = document.getElementById('area-drop');
areaDrop.addEventListener('dragover', (e) => { e.preventDefault(); areaDrop.classList.add('arraste-sobre'); });
areaDrop.addEventListener('dragleave', () => areaDrop.classList.remove('arraste-sobre'));
areaDrop.addEventListener('drop', (e) => {
  e.preventDefault();
  areaDrop.classList.remove('arraste-sobre');
  if (e.dataTransfer.files[0]) enviarArquivo(e.dataTransfer.files[0]);
});

function enviarArquivo(arquivo) {
  if (!conexaoDados || !conexaoDados.open) { alert('Aguarde o suporte se conectar primeiro.'); return; }
  const id = 'f' + Date.now();
  listaArquivos.prepend(criarLinhaArquivo(id, arquivo.name, 'enviando'));
  conexaoDados.send({ tipo: 'inicio-arquivo', id, nome: arquivo.name, tamanho: arquivo.size, mime: arquivo.type });

  const leitor = new FileReader();
  let offset = 0;
  function lerProximoPedaco() { leitor.readAsArrayBuffer(arquivo.slice(offset, offset + TAMANHO_PEDACO)); }
  leitor.onload = () => {
    conexaoDados.send({ tipo: 'pedaco-arquivo', id, dados: leitor.result });
    offset += leitor.result.byteLength;
    atualizarProgresso(id, offset / arquivo.size);
    if (offset < arquivo.size) { lerProximoPedaco(); }
    else { conexaoDados.send({ tipo: 'fim-arquivo', id }); marcarConcluido(id, 'enviado'); }
  };
  lerProximoPedaco();
}

function tratarDadoRecebido(dado) {
  if (dado.tipo === 'controle') {
    if (wsAgente && wsAgente.readyState === WebSocket.OPEN) {
      wsAgente.send(JSON.stringify(dado.comando));
    }
    return;
  }
  if (dado.tipo === 'inicio-arquivo') {
    recebendo[dado.id] = { nome: dado.nome, tamanho: dado.tamanho, mime: dado.mime, pedacos: [], recebido: 0 };
    listaArquivos.prepend(criarLinhaArquivo(dado.id, dado.nome, 'recebendo'));
  } else if (dado.tipo === 'pedaco-arquivo') {
    const r = recebendo[dado.id]; if (!r) return;
    r.pedacos.push(dado.dados); r.recebido += dado.dados.byteLength;
    atualizarProgresso(dado.id, r.recebido / r.tamanho);
  } else if (dado.tipo === 'fim-arquivo') {
    const r = recebendo[dado.id]; if (!r) return;
    const blob = new Blob(r.pedacos, { type: r.mime || 'application/octet-stream' });
    marcarConcluido(dado.id, 'recebido', URL.createObjectURL(blob), r.nome);
    delete recebendo[dado.id];
  }
}

function criarLinhaArquivo(id, nome, statusTexto) {
  const li = document.createElement('li');
  li.id = 'arquivo-' + id;
  li.innerHTML = `<span>${nome}</span><div class="barra"><div id="barra-${id}"></div></div><span id="status-${id}" style="color:var(--text-dim); font-size:12px;">${statusTexto}</span>`;
  return li;
}
function atualizarProgresso(id, fracao) {
  const barra = document.getElementById('barra-' + id);
  if (barra) barra.style.width = Math.min(100, Math.round(fracao * 100)) + '%';
}
function marcarConcluido(id, texto, url, nome) {
  const statusEl = document.getElementById('status-' + id);
  if (!statusEl) return;
  statusEl.innerHTML = url ? `<a href="${url}" download="${nome}">baixar</a>` : texto;
}

iniciarPeer();
</script>
</body>
</html>
"""

MAPA_TECLAS = {
    "Enter": "enter", "Backspace": "backspace", "Tab": "tab", "Escape": "esc",
    "ArrowUp": "up", "ArrowDown": "down", "ArrowLeft": "left", "ArrowRight": "right",
    "Delete": "delete", " ": "space", "Home": "home", "End": "end",
    "PageUp": "pageup", "PageDown": "pagedown", "CapsLock": "capslock",
    "Meta": NOME_TECLA_META, "Control": "ctrl", "Alt": "alt", "Shift": "shift",
    "PrintScreen": "printscreen",
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
    async for mensagem in websocket:
        try:
            executar_comando(json.loads(mensagem))
        except Exception as e:
            print("[!] Erro ao executar comando:", e)


async def rodar_agente():
    async with websockets.serve(tratar_conexao, "localhost", 8765):
        await asyncio.Future()


def iniciar_agente_em_thread():
    # roda o servidor websocket numa thread separada pra nao travar a janela do tkinter
    def alvo():
        asyncio.run(rodar_agente())
    t = threading.Thread(target=alvo, daemon=True)
    t.start()
    return t


def abrir_pagina_atendimento():
    caminho_temp = os.path.join(tempfile.gettempdir(), "atendimento_cliente.html")
    with open(caminho_temp, "w", encoding="utf-8") as f:
        f.write(PAGINA_HTML)
    # Path.as_uri() monta a URL certa tanto no Windows (C:\...) quanto no Mac/Linux
    webbrowser.open(Path(caminho_temp).as_uri())
    return caminho_temp


def mostrar_sobre():
    messagebox.showinfo("Sobre", "Atendimento remoto\nDesenvolvido por Wesley Walter")


def main():
    iniciar_agente_em_thread()
    caminho_pagina = abrir_pagina_atendimento()

    janela = tk.Tk()
    janela.title("Atendimento em andamento")
    janela.geometry("380x200")
    janela.resizable(False, False)

    tk.Label(
        janela, text="Atendimento em andamento",
        font=("Segoe UI", 13, "bold")
    ).pack(pady=(18, 6))

    tk.Label(
        janela,
        text="A página de atendimento foi aberta no seu navegador.\n"
             "Deixe esta janela aberta durante o suporte.",
        font=("Segoe UI", 10), justify="center"
    ).pack(pady=(0, 14))

    def encerrar():
        if messagebox.askyesno("Encerrar", "Encerrar o atendimento agora?"):
            try:
                os.remove(caminho_pagina)
            except OSError:
                pass
            janela.destroy()
            os._exit(0)

    frame_botoes = tk.Frame(janela)
    frame_botoes.pack()

    tk.Button(
        frame_botoes, text="Encerrar atendimento", command=encerrar,
        bg="#e0685b", fg="white", font=("Segoe UI", 10, "bold"),
        padx=12, pady=8, relief="flat"
    ).pack(side="left", padx=4)

    tk.Button(
        frame_botoes, text="Sobre", command=mostrar_sobre,
        font=("Segoe UI", 10), padx=12, pady=8, relief="flat"
    ).pack(side="left", padx=4)

    janela.protocol("WM_DELETE_WINDOW", encerrar)
    janela.mainloop()


if __name__ == "__main__":
    main()
