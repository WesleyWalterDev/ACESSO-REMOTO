# Suporte Remoto — Cliente / Suporte

Desenvolvido por **Wesley Walter**.

Sistema de suporte técnico direto pelo navegador: o suporte vê a tela do
cliente, pode controlar mouse e teclado, e os dois trocam arquivos — tudo
sem o suporte precisar instalar nada.

## Novidades desta versão

### Atalhos do Windows (Win, Alt+Tab, etc.)

Não é possível "capturar" combinações de teclado do sistema pelo navegador —
o próprio navegador ou o Windows intercepta antes de chegar na página (é
assim em qualquer ferramenta baseada em navegador, não é uma limitação
nossa). A solução foi adicionar **botões prontos** no painel de suporte,
logo acima do vídeo: Win, Alt+Tab, Win+D, Win+E, Ctrl+Esc e Print Screen.
Eles simulam o atalho diretamente na máquina do cliente sem depender de
capturar a tecla física.

**Exceção que não tem como resolver:** Ctrl+Alt+Delete não pode ser simulado
por nenhum software, nem por ferramentas como AnyDesk/TeamViewer — o Windows
bloqueia isso de propósito por segurança (é um recurso de hardware, não dá
pra falsificar). Se precisar reiniciar sessão/trocar usuário, isso tem que
ser feito fisicamente na máquina do cliente.

### A barra "Parar partilha / Ocultar"

Essa barra é do **Chrome do cliente**, não é nosso código — ela aparece
automaticamente sempre que uma aba está compartilhando a tela, como aviso de
segurança do próprio navegador (não dá pra remover via código). No seu teste
apareceu porque você testou cliente e suporte na mesma máquina; em uso real,
com máquinas separadas, ela só aparece na tela do **cliente** (que pode
clicar em "Ocultar" pra minimizá-la) — na sua tela, como suporte, ela nunca
aparece.

### Múltiplos clientes ao mesmo tempo (tipo AnyDesk)

O `suporte.html` agora tem uma barra lateral com as máquinas salvas e abas
no topo pra alternar entre atendimentos abertos ao mesmo tempo — cada sessão
mantém sua própria tela, controle e arquivos isolados. Pra adicionar uma
máquina: preencha um nome (o que quiser) e o código dela na barra lateral e
clique em "Salvar e conectar". Da próxima vez, é só clicar nela na lista.

### Delay ao mexer o mouse

O motivo do atraso: antes, cliques, teclas, arquivos e a posição do mouse
disputavam o mesmo canal de rede — se um arquivo grande estivesse sendo
enviado, os comandos de mouse ficavam "na fila" atrás dele. Agora existem
dois canais separados: um rápido (sem garantia de entrega, só pra posição do
mouse — perder uma posição não faz diferença, a próxima já corrige) e um
confiável (pra cliques, teclas e arquivos, que não podem se perder). Isso
deve reduzir bastante o atraso. O que ainda pode causar lentidão, e não tem
como resolver por software, é a **qualidade da internet das duas pontas** —
quanto mais distante/instável a conexão, mais delay, isso é física de rede,
não do programa.

### Executável do suporte, com conexões salvas

Agora existe o `suporte_app.py`, no mesmo estilo do `iniciar_atendimento.py`:
sobe um servidor só nesta máquina (não é acessível de fora) que guarda as
conexões salvas em `~/.suporte_wesley/conexoes.json`, e abre o painel
completo no navegador sozinho.

**Para gerar o executável do suporte:**

No Windows, junte `suporte_app.py` + `build_suporte_windows.bat` na mesma
pasta e dê dois cliques no `.bat`. Gera `dist\Suporte.exe`.

No Mac, junte `suporte_app.py` + `build_suporte_mac.sh`, rode:
```bash
chmod +x build_suporte_mac.sh
./build_suporte_mac.sh
```
Gera `dist/Suporte`.

Mande esse único arquivo pra quem for atender — ele não precisa de Python
instalado, e as conexões salvas continuam lá mesmo depois de fechar e abrir
o programa de novo.

### Confirmação de que as máquinas salvas realmente persistem

Testei simulando duas execuções separadas do programa (fechar de verdade e
abrir de novo, sem nenhuma memória da execução anterior) — os dados
continuaram lá. Além disso, agora a própria janela do `suporte_app.py` mostra
quantas máquinas estão salvas e o caminho exato do arquivo
(`~/.suporte_wesley/conexoes.json`), com um botão "Ver arquivo de dados
salvos" pra você conferir com os próprios olhos quando quiser.

### Instalador de verdade (Setup.exe com atalho e desinstalador)

O `Suporte.exe` gerado pelo `build_suporte_windows.bat` já funciona sozinho
(só dar dois cliques), mas é um arquivo "solto" — não aparece em
"Programas e Recursos", não cria atalho automaticamente. Pra ter um
instalador de verdade (tipo instalar qualquer programa comum do Windows):

1. Baixe e instale o **Inno Setup** (gratuito, oficial, usado por muitos
   softwares conhecidos): https://jrsoftware.org/isdl.php — é só rodar o
   instalador dele uma vez, igual você fez com o Python.
2. Rode o `build_suporte_windows.bat` primeiro (precisa existir
   `dist\Suporte.exe`).
3. Abra o arquivo `suporte_installer.iss` com o Inno Setup (clique com o
   botão direito nele → "Abrir com" → Inno Setup, ou já abre direto se
   associou na instalação).
4. Clique em **Compile** (ou no menu Build → Compile).
5. Pronto: o instalador final fica em `Output\SuporteSetup.exe`.

Esse `SuporteSetup.exe` é o que você distribui daqui pra frente — quando
alguém roda ele, instala o programa em "Arquivos de Programas", cria atalho
no Menu Iniciar (e na Área de Trabalho, se marcar a opção), e aparece
certinho em "Programas e Recursos" pra desinstalar se precisar.

## Os arquivos

| Arquivo | Roda em | Precisa instalar algo? |
|---|---|---|
| `iniciar_atendimento.py` | Máquina do **cliente** | Sim, uma vez (Python + 2 libs) — depois é só abrir |
| `suporte_app.py` | Máquina do **suporte** | Sim, uma vez (Python) — depois é só abrir |
| `suporte_installer.iss` | Seu computador (pra gerar o instalador) | Sim, Inno Setup — só se quiser o Setup.exe de verdade |

O `iniciar_atendimento.py` já faz tudo sozinho: sobe o agente de controle
remoto **e** abre a página de atendimento no navegador automaticamente. O
cliente não precisa mais abrir dois programas separados nem entender o que é
um "agente" — só roda um programa e pronto.

(Os arquivos `usuario.html` e `agente_controle.py` separados continuam
disponíveis, caso você prefira rodar cada peça manualmente ou entender como
funciona por dentro — mas para o dia a dia, use o `iniciar_atendimento.py`.)

## Distribuindo para vários clientes (Windows e Mac) — seu caso

Como você tem acesso a um computador Windows e a um Mac com Python, o processo
é: gerar o executável **uma vez em cada sistema**, e depois usar esse mesmo
arquivo gerado para **todos** os clientes daquele sistema (não precisa gerar
de novo para cada cliente).

### Passo 1 — Gere o `.exe` no seu Windows

Copie estes 3 arquivos para uma pasta no seu Windows:
- `iniciar_atendimento.py`
- `requirements_agente.txt`
- `build_cliente_windows.bat`

Dê dois cliques em `build_cliente_windows.bat`. Ele vai instalar o que for
preciso e gerar o arquivo:
```
dist\Atendimento.exe
```
Pronto — **esse único arquivo `Atendimento.exe`** é tudo que você precisa
mandar para qualquer cliente Windows. Guarde-o.

### Passo 2 — Gere o app no seu Mac

Copie os mesmos 3 arquivos (trocando o `.bat` pelo `.sh`) para uma pasta no
seu Mac:
- `iniciar_atendimento.py`
- `requirements_agente.txt`
- `build_cliente_mac.sh`

No Terminal, dentro dessa pasta:
```bash
chmod +x build_cliente_mac.sh
./build_cliente_mac.sh
```
Isso gera:
```
dist/Atendimento
```
Esse é o arquivo que você manda para qualquer cliente Mac.

### Passo 3 — Atender qualquer cliente, dali em diante

- Cliente com **Windows** → manda `Atendimento.exe` (por e-mail, WhatsApp,
  Google Drive, o que for mais fácil). Ele só dá dois cliques.
- Cliente com **Mac** → manda o `Atendimento` gerado no passo 2. Ele dá dois
  cliques (na primeira vez, se o Mac bloquear por "desenvolvedor não
  identificado", ele clica com o botão direito no arquivo e escolhe "Abrir").

Nenhum dos dois precisa ter Python instalado — o executável já leva tudo
embutido. Você só repete os passos 1 e 2 se um dia quiser atualizar o
programa; para atender um cliente novo, é só reenviar o arquivo que você já
gerou.



### No cliente (a máquina que vai ser acessada) — jeito mais simples

Dê os arquivos `instalar_e_iniciar.bat` (Windows) ou `instalar_e_iniciar.command`
(Mac) + `iniciar_atendimento.py` + `requirements_agente.txt` para o cliente
(pasta zipada, pen-drive, e-mail — como preferir, desde que fiquem juntos na
mesma pasta).

1. O cliente dá **dois cliques** no instalador (`.bat` no Windows,
   `.command` no Mac).
2. Ele sozinho verifica se o Python está instalado (e leva para a página de
   download se não estiver), instala as bibliotecas que faltam, e já abre o
   atendimento — navegador + janelinha de status.
3. O código de 6 caracteres aparece na página — o cliente te passa esse código.

No Mac, na primeira vez, o Finder pode bloquear com "desenvolvedor não
identificado" — nesse caso, o cliente clica com o botão direito no arquivo
`.command` e escolhe "Abrir" (só precisa fazer isso uma vez).

**Importante — sobre "gerar sozinho o `.exe` já pronto":** não existe forma de
eu compilar um executável Windows/Mac funcional a partir deste ambiente
Linux — isso sempre precisa ser feito rodando o PyInstaller na própria
máquina de destino (seção mais abaixo). O instalador de duplo clique acima é
o caminho mais próximo disso sem exigir isso do cliente: ele nunca abre um
terminal manualmente nem digita comando nenhum, só clica duas vezes.

### No cliente — passo a passo manual (alternativa)

1. Instale as dependências (só precisa fazer isso **uma vez**):
   ```bash
   pip install -r requirements_agente.txt
   ```
2. Rode:
   ```bash
   python3 iniciar_atendimento.py
   ```
   Isso abre uma janelinha de status **e** o navegador com a página de
   atendimento automaticamente.
3. Na página que abriu, vai aparecer um código de 6 caracteres — **passe
   esse código para o suporte** (WhatsApp, telefone, etc.).
4. Quando terminar, clique em "Encerrar atendimento" na janelinha (ou apenas
   feche-a).

Quer que o cliente nem precise ter Python instalado? Veja a seção
**"Gerando um executável"** abaixo — depois de gerado, ele só dá dois
cliques num arquivo `.exe` (Windows) ou app (Mac) e pronto.

### No suporte (a máquina de quem vai atender)

1. Abra `suporte.html` no navegador — não precisa instalar nada.
2. Digite o código que o cliente te passou e clique em **Conectar**.
3. Assim que o cliente clicar em "Iniciar compartilhamento de tela", a tela dele aparece automaticamente.
4. Para poder mexer no mouse/teclado da máquina dele, marque a caixinha
   **"Habilitar controle de mouse e teclado"** acima do vídeo, e clique na tela para focar.
   - Mova o mouse, clique, dê scroll e digite normalmente — tudo isso é executado de verdade na máquina do cliente.
5. Use a seção de arquivos para mandar algo para o cliente (ex: um instalador) ou receber algo que ele te enviar.

## O que cada parte faz

- **`usuario.html`**: só compartilha a tela e arquivos, e repassa os comandos de
  controle (que chegam pela conexão do navegador) para o agente local rodando
  na própria máquina.
- **`agente_controle.py`**: fica escutando em `ws://localhost:8765`, esperando
  o `usuario.html` se conectar. Quando chega um comando (mover mouse, clicar,
  digitar), ele executa de verdade usando a biblioteca `pyautogui`.
- **`suporte.html`**: mostra a tela do cliente e captura os movimentos do
  mouse/teclado feitos *sobre o vídeo*, convertendo a posição para a
  resolução real da tela do cliente antes de enviar.

## Segurança — leia antes de usar

- **O código de 6 caracteres é a única "senha" dessa sessão.** Trate-o como
  algo sensível — não poste em lugar público. Quem tiver o código pode se
  conectar e controlar a máquina do cliente enquanto o `usuario.html` estiver
  aberto.
- O controle remoto só funciona enquanto o cliente **decidir manter o
  `agente_controle.py` rodando** — ele pode fechar o terminal a qualquer
  momento para cortar o controle imediatamente (a visualização da tela e
  arquivos também param se ele fechar a aba do navegador).
- No **Mac**, na primeira vez, o sistema vai pedir para liberar permissões de
  **Gravação de Tela** (para o `getDisplayMedia` funcionar) e de
  **Acessibilidade** (para o `pyautogui` conseguir mover o mouse/teclado) em
  Ajustes do Sistema > Privacidade e Segurança.
- Isso é um projeto pessoal — não é um produto auditado como
  TeamViewer/AnyDesk. Bom para uso próprio entre você e alguém de confiança,
  não recomendado para dar suporte a desconhecidos ou em ambiente corporativo.

## Gerando um executável do cliente (recomendado)

Assim o cliente não precisa nem ter Python instalado — só dois cliques.

**No Windows** (rode na própria máquina Windows do cliente):
```
build_cliente_windows.bat
```
Gera `dist\Atendimento.exe` — sem janela de terminal, só a janelinha de status.

**No Mac** (rode na própria máquina Mac do cliente):
```bash
chmod +x build_cliente_mac.sh
./build_cliente_mac.sh
```
Gera `dist/Atendimento`.

Isso precisa ser feito **na própria máquina de destino** — não dá para gerar
um `.exe` do Windows a partir de um Mac ou vice-versa.

