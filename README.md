# Cognit

Quiz de tecnologia, usabilidade e design feito em **Python com Pygame**, seguindo as cores, os
cartões e os personagens das telas da pasta `prototipo`.

## Jogar no computador

Use Python 3.11 ou superior. No terminal, dentro da pasta do projeto:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe jogo/main.py
```

Se usar outra versão instalada, troque `py -3.11` por `python` no primeiro
comando. Os demais comandos continuam iguais. Não é necessário ativar o
ambiente virtual no PowerShell.

No Linux/macOS, crie o ambiente com `python3 -m venv .venv` e use
`.venv/bin/python` no lugar de `.\.venv\Scripts\python.exe`.

O pacote instalado é `pygame-ce`, a edição comunitária do Pygame compatível
com o Pygbag. O código usa **`import pygame`**, e todas as telas e interações
do jogo são feitas com essa biblioteca. Não instale `pygame` e `pygame-ce`
juntos no mesmo ambiente, pois ambos usam o mesmo nome de importação.

## Regras

- A partida começa com **3 vidas**.
- Cada tema tem **10 perguntas**, em ordem de dificuldade: de Iniciante até Desafio final.
- Cada acerto aumenta o progresso em 10% e libera a próxima pergunta.
- Cada erro desconta uma vida. A pergunta se mantém e a alternativa errada
  fica desativada; escolha outra para continuar.
- O relógio começa em **45 segundos**, diminui **3 segundos por pergunta**
  e tem piso de **12 segundos**. Ao errar uma opção, o prazo restante é mantido.
- Tempo esgotado custa uma vida e permite tentar a mesma pergunta com um
  novo prazo. Feedback e confirmação de saída pausam o relógio no modo solo.
- A dica é liberada depois de **8 segundos**: clique/toque no cérebro.
  Ela aparece somente após o clique/toque.
- Ao acertar todas, você vence. Ao perder a terceira vida, a partida acaba.
- Na vitória solo, o resultado mostra a barra totalmente preenchida em **100%**.
- As telas de acerto explicam a resposta. Reiniciar recupera as três vidas.

Clique/toque nos botões ou use **Tab/setas** para navegar e **Enter/espaço**
para confirmar. Nas perguntas, **A/B/C/D** ou **1/2/3/4** selecionam as opções.
**Esc** permite sair da pergunta com confirmação. A janela pode ser
redimensionada e mantém a proporção do protótipo.

## Música e tela de perguntas

A tela concentra a posição da pergunta e o tempo em uma única linha. O
enunciado aparece direto no fundo, o código usa um único bloco e as opções
têm letras e textos mais leves. A dica fica no rodapé e aparece ao tocar
no cérebro depois da espera. Os pontos são consultados no resultado da rodada.

Uma trilha instrumental original de **20 segundos** toca em repetição, com
volume baixo. Clique no **alto-falante** ou pressione **M** para desligar e
religar o som. A escolha é mantida durante a sessão, inclusive ao trocar de tela.
No navegador, o som começa depois do primeiro clique/toque ou tecla, respeitando
o bloqueio de reprodução automática. [Áudio no Pygbag](https://pygame-web.github.io/wiki/pygbag-code/).

Para ajustar, edite `MUSICA_ATIVA` e `VOLUME_MUSICA` em `jogo/config.py`.
A reprodução fica isolada em `jogo/audio.py`; se o aparelho não tiver saída
de áudio disponível, o jogo continua funcionando.

O arquivo `jogo/assets/musica_fundo.ogg` já está pronto. Para recriar ou
editar a composição (opcional, sem alterar as dependências para jogar):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-audio.txt
.\.venv\Scripts\python.exe scripts/gerar_musica.py
```

Os temas **Tecnologia** e **UX e Design** estão disponíveis nos modos solo e
amigos, usando o mesmo catálogo e as mesmas perguntas de `jogo/temas.py`.
UX e Design aborda usabilidade, wireframes, protótipos, testes com usuários,
Figma, Auto Layout, componentes e acessibilidade de formulários.
As referências de cada questão estão nos comentários de `jogo/perguntas_ux_design.py`,
incluindo a [documentação do Figma](https://help.figma.com/hc/en-us/articles/360040314193-Guide-to-prototyping-in-Figma),
as orientações de [usabilidade da NN/g](https://www.nngroup.com/articles/usability-101-introduction-to-usability/)
e os guias de [formulários da W3C](https://www.w3.org/WAI/tutorials/forms/labels/).
Login, criação de quizzes
pela interface e salvamento entre sessões ainda não estão implementados.

## Disputar com amigos

O botão **Jogar com amigos** abre o formulário para criar ou entrar em uma sala.
A disputa usa um servidor compartilhado; cada jogador pode usar seu próprio
computador ou o jogo exportado no navegador.

### No mesmo computador

Abra um terminal na raiz e inicie o servidor (somente biblioteca padrão Python):

```powershell
.\.venv\Scripts\python.exe servidor.py
```

Em outros dois terminais, abra uma instância do jogo em cada um:

```powershell
.\.venv\Scripts\python.exe jogo/main.py
```

1. Nos dois jogos, clique em **Jogar com amigos**. A conexão é automática.
2. Na aba **Criar sala**, o anfitrião informa seu nome, personaliza o cérebro,
   clica em **Alterar** ao lado de **Tema da sala**, seleciona um dos temas
   cadastrados e clica em **Criar minha sala**. O cartão mostra o tema escolhido.
3. Na aba **Entrar**, o amigo informa seu nome, escolhe seu cérebro, digita
   o código de seis dígitos e clica em **Vamos jogar**.
4. Com pelo menos dois participantes, o anfitrião clica em **Iniciar disputa**.

`http://localhost:8765` é o endereço padrão da API de salas, configurado em
`jogo/config.py`. O endereço não é exibido no menu. Abri-lo no navegador mostra o status
do servidor e as instruções de acesso. Para abrir a janela do jogo, execute
`python jogo/main.py`; para jogar no navegador, siga a seção **Jogar no navegador**
e acesse `http://localhost:8000`. Após atualizar `servidor.py`, encerre o servidor
com `Ctrl+C` e execute-o novamente para carregar as alterações.

No desktop, clique em um campo e digite. **Enter** encerra a edição,
**Ctrl+V** cola e **Ctrl+A** limpa o campo. No navegador, tocar em um campo
abre um diálogo nativo, incluindo o teclado do celular.

### Em computadores/celulares na mesma rede

Na máquina que será o servidor:

```powershell
.\.venv\Scripts\python.exe servidor.py --host 0.0.0.0 --port 8765
```

Execute `ipconfig` e encontre o IPv4 da conexão usada, por exemplo
`192.168.1.20`. Para configurar cada cliente desktop antes de abrir o jogo:

```powershell
$env:COGNIT_SERVIDOR = "http://192.168.1.20:8765"
.\.venv\Scripts\python.exe jogo/main.py
```

Também é possível editar `SERVIDOR_PADRAO` em `jogo/config.py`.
`localhost` representa o próprio aparelho.
Se o Windows solicitar, permita a conexão do Python na rede privada.
O servidor precisa permanecer aberto durante a disputa.

Para celulares, exporte o jogo conforme a seção de navegador, execute
`python -m http.server 8000 --bind 0.0.0.0 --directory jogo/build/web`
e abra `http://192.168.1.20:8000/?servidor=http://192.168.1.20:8765`.
O parâmetro `servidor` configura a conexão sem exibir um campo técnico no menu.

### Regras das salas

- De **2 a 12 jogadores**, com apelidos únicos por sala; o anfitrião também joga.
- Cada pessoa escolhe um cérebro: Cognit, GTA VI, Zelda, Cruzeiro, Naruto ou
  Harry Potter. São variantes vetoriais do mascote do Cognit.
- No lobby, toque no seu cérebro ou em **Estou pronto** para sinalizar que
  está pronto. As marcações aparecem para todos; o anfitrião decide quando iniciar.
- Todos recebem a mesma pergunta e o mesmo prazo, controlados pelo servidor.
- Há **uma tentativa por pergunta**, sem eliminação por vidas.
- A rodada termina quando todos respondem ou o tempo acaba. O resultado
  individual aparece com acerto/erro/tempo esgotado e uma contagem
  animada de pontos. Depois, a classificação destaca os cinco primeiros e
  mantém sua posição visível mesmo fora desse grupo. **Ver explicação** abre
  o gabarito comentado; o anfitrião libera a próxima pergunta.
- Um acerto vale de **500 a 1.000 pontos**, conforme o tempo restante. Pedir
  a dica após a espera desconta **200 pontos** desse acerto, uma única vez.
  Erro ou ausência de resposta vale zero.
- Pontos da rodada, resultado e acertos só são publicados ao encerrar a rodada.
  Após enviar a resposta, uma tela de espera mostra quantos já responderam.
  Antes do encerramento, os totais exibidos ainda são os da rodada anterior.
- A classificação usa pontos e, no desempate, quantidade de acertos.
  Igualdade nos dois critérios é mostrada como empate na liderança.
- No final, um pódio animado revela os três primeiros e destaca quarto e
  quinto. Toque nos avatares para consultar pontos/acertos, ou use **Rever pódio**
  para repetir a animação. A posição de quem está fora do top 5 continua visível.
- A confirmação de saída **não pausa** a sala. Ao sair, o jogador é removido
  do placar; se for anfitrião, outro assume. Se o anfitrião perder a conexão
  por 30 segundos, um participante conectado assume e os pontos são mantidos.
- Falhas temporárias de conexão são sinalizadas e o cliente tenta sincronizar
  novamente. Fechar/recarregar a página perde a sessão desse jogador; a
  transferência automática do anfitrião mantém a disputa dos demais.
- Não é possível entrar após o início. Salas vazias são removidas e salas
  sem atividade expiram após duas horas.

As salas ficam **em memória**: reiniciar o servidor apaga salas e placares.
Execute apenas uma instância do servidor, pois processos distintos não
compartilham esses dados.

### Usar pela internet

O site estático do Render continua servindo o jogo. Para salas entre redes
diferentes, é necessário hospedar também `servidor.py` em um serviço Python
acessível aos participantes. Configure o serviço para executar
`python servidor.py --host 0.0.0.0 --port PORTA_DO_SERVICO`, em uma única
instância, atrás do proxy HTTPS da hospedagem. Nenhuma hospedagem é criada
automaticamente ao executar o projeto.

Configure o endereço HTTPS desse serviço em `SERVIDOR_PADRAO` ou em
`COGNIT_SERVIDOR`, por exemplo `https://salas.seu-dominio.com`.
Uma página HTTPS precisa de uma API HTTPS.
É possível compartilhar o site como
`https://jogo.seu-dominio.com/?servidor=https://salas.seu-dominio.com`.

No Render, crie um **New → Web Service** no mesmo repositório e configure:

| Campo | Valor |
| --- | --- |
| Language | `Python 3` |
| Root Directory | Vazio, pois `servidor.py` está na raiz |
| Build Command | `python --version` |
| Start Command | `python -u servidor.py --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/saude` |
| Instâncias | Uma |

O servidor usa apenas a biblioteca padrão; as dependências do Pygame são do
jogo. O Render fornece a variável `PORT` e o endereço HTTPS da API.
[Configuração de Web Services](https://render.com/docs/web-services).
Depois da publicação, abra `https://SEU-SERVIDOR.onrender.com/saude` e confira
`{"ok": true}`. Compartilhe o endereço do jogo com o parâmetro
`?servidor=https://SEU-SERVIDOR.onrender.com`; a versão web lê essa URL no
carregamento. No desktop, defina `COGNIT_SERVIDOR` antes de abrir o jogo.

No plano Free, o serviço suspende após 15 minutos sem tráfego e pode levar
cerca de um minuto para despertar. Abra `/saude` e espere a resposta antes
de entrar no jogo. Reinícios e novas publicações apagam as salas em memória.
[Limites do plano gratuito](https://render.com/docs/free).

O adaptador HTTP incluído usa `http.server`, adequado para demonstrações e
redes de amigos. Uma operação pública com grande volume deve substituir
esse adaptador por um servidor de produção e usar armazenamento compartilhado;
as regras estão isoladas em `jogo/salas.py` para facilitar essa evolução.
[Limites de http.server](https://docs.python.org/3.11/library/http.server.html#security-considerations).
Para restringir quais sites acessam a API pelo navegador, use
`--origem https://jogo.seu-dominio.com` (pode repetir); sem essa opção, as
origens são liberadas para facilitar testes locais.

Os níveis 6 a 10 continuam a sequência com consultas a APIs via GET,
imagens e containers Docker, escala horizontal na cloud, DNS e TCP.
Todos possuem alternativas de A a D, explicações e
referências técnicas nos comentários de `jogo/perguntas.py`.

## Onde personalizar

| Arquivo | O que mudar |
| --- | --- |
| `jogo/perguntas.py` | Perguntas de Tecnologia, alternativas, resposta correta, explicação e dica |
| `jogo/perguntas_ux_design.py` | Perguntas de UX e Design, com dicas, explicações e fontes |
| `jogo/config.py` | Nome, vidas, tempos, limites de salas, cores e medidas |
| `jogo/tempo.py` | Cálculo do prazo decrescente e da espera pela dica |
| `jogo/temas.py` | Cadastro dos temas disponíveis; os menus acompanham o catálogo |
| `jogo/partida.py` | Regras solo: vidas, tempo, dica, acertos e progresso |
| `jogo/main.py` | Janela, eventos, navegação e loop principal |
| `jogo/visuais_solo.py` | Menus, perguntas, feedback e resultado do modo solo |
| `jogo/interface.py` | Aparência dos botões, cartões, texto e corações |
| `jogo/audio.py` | Carregamento, volume, pausa e repetição da música |
| `scripts/gerar_musica.py` | Composição e geração da trilha original em OGG |
| `jogo/telas_pergunta.py` | Enunciado, cronômetro e cérebro clicável dos dois modos |
| `jogo/telas_sala.py` | Ações de salas, perfil e sincronização da interface |
| `jogo/visuais_sala.py` | Menu, lobby, espera, feedback, top 5 e pódio animado |
| `jogo/visuais_temas.py` | Cartões de tema com ícone, descrição e versão compacta para salas |
| `jogo/avatares.py` | Nomes, identificadores e arquivos dos cérebros disponíveis |
| `scripts/gerar_avatares.py` | Recria os seis SVGs personalizados a partir do mascote original |
| `jogo/rede.py` | Cliente HTTP assíncrono para desktop e navegador |
| `jogo/salas.py` | Regras de salas, participantes, prazos e pontuação no servidor |
| `servidor.py` | API HTTP: valida JSON, controla origens e chama as regras das salas |
| `jogo/assets/` | Logotipo, mascotes e fontes |
| `web/cognit.tmpl` | Página que carrega a exportação no navegador |
| `exportar_web.py` | Comando de geração da versão web |

Por exemplo, uma pergunta em `jogo/perguntas.py` tem esta estrutura:

```python
{
    "dificuldade": "Iniciante",
    "enunciado": "Qual destes é um sistema operacional?",
    "alternativas": ["Chrome", "Android", "Excel"],
    "correta": 1,
    "explicacao": "O Android gerencia os recursos do aparelho.",
    "dica": "Ele gerencia o aparelho e permite instalar outros aplicativos.",
},
```

O índice começa em zero: **0 = A, 1 = B, 2 = C, 3 = D**. Cada pergunta pode
ter de duas a quatro alternativas. Para mostrar um trecho de código,
adicione o campo `"codigo": "linha 1\nlinha 2"`.

A ordem da lista determina a progressão. Se adicionar ou remover perguntas,
o total e o percentual se ajustam automaticamente. Mantenha os textos curtos
para caberem nos cartões. As perguntas não são embaralhadas, para preservar
a dificuldade crescente.

Para mudar as vidas, edite `VIDAS_INICIAIS = 3` em `config.py`. Para mudar
os personagens, edite os SVGs da pasta `assets`, mantendo seus nomes.
Também é possível usar PNGs: remova o SVG correspondente e substitua seu
PNG por uma imagem de boa resolução. Os protótipos originais foram preservados.

Em `config.py`, ajuste `TEMPO_INICIAL`, `REDUCAO_POR_PERGUNTA`,
`TEMPO_MINIMO` e `ESPERA_DICA`. A espera da dica é limitada à metade do
prazo, para continuar utilizável ao configurar perguntas curtas.
Para criar outro tema, adicione uma entrada a `TEMAS` em `temas.py`, com
um identificador, um nome e uma lista de perguntas com a estrutura acima.
Os campos opcionais `descricao` e `icone` personalizam o cartão nos dois
modos. Tecnologia usa `"icone": "tecnologia"` e UX e Design usa
`"icone": "ux_design"`. A tabela de ícones não cadastra temas: o catálogo único
é `TEMAS`, compartilhado pelo modo solo e pelo servidor de salas. Para adicionar uma ilustração,
coloque seu SVG em `assets` e cadastre-o em `ICONES_TEMA` no `visuais_temas.py`.
O modo solo exibe dois cartões por página, com navegação se houver mais temas.
Os dois temas cadastrados têm ícones próprios. Temas com uma lista vazia não
aparecem como opções. Depois de cadastrar um tema, reinicie o servidor e
reabra o menu de amigos: ele consulta o catálogo novamente.

Para mudar a duração da tela de resultado de cada rodada, edite
`DURACAO_FEEDBACK_RODADA` em `config.py` (padrão: 2,5 segundos). Também é
possível avançar diretamente usando **Ver classificação**. As animações são
calculadas por tempo, sem pausas bloqueantes no loop do jogo.

As posições e os tamanhos no código continuam seguindo o protótipo de
390 × 844. `Interface` converte essas medidas para os pixels reais da tela.
As fontes e os SVGs são desenhados diretamente nessa resolução, evitando
ampliar uma imagem pequena e desfocar a interface em celulares.

## Como explicar o código na apresentação

1. `main.py` abre a janela e executa o loop do jogo.
2. Cada quadro lê os eventos do mouse, toque ou teclado.
3. A ação selecionada chama uma regra de `Partida`, que guarda as vidas,
   os acertos e a pergunta atual.
4. `VisuaisSolo` ou `VisuaisSala` escolhe os elementos da tela e usa `Interface` para desenhá-los.
5. O desenho é ajustado ao tamanho da janela e exibido.

`Partida` não depende do Pygame: as regras podem ser lidas e testadas
separadamente dos desenhos. O `await asyncio.sleep(0)` no loop principal
cede a execução ao navegador e permite usar o mesmo jogo na versão web.

No modo de amigos, `TelasSala` transforma as ações em requisições de
`ClienteSalas`, aplica as respostas e mantém a interface sincronizada.
`servidor.py` recebe HTTP e chama `GerenciadorSalas`: validação, dicas,
avanço de rodada e respostas ficam em métodos próprios de `salas.py`.
`VisuaisSala` apenas desenha o estado recebido. O catálogo de temas e a
política de tempo são compartilhados pelos dois modos.

Para editar o projeto, comece pelo arquivo da responsabilidade desejada:
conteúdo em `temas.py` e `perguntas*.py`, regras em `partida.py`/`salas.py`,
desenhos em `visuais_*.py` e componentes reutilizáveis em `interface.py`.

## Jogar no navegador

Uma janela Pygame aberta em um servidor não aparece no navegador de quem
acessa o site. Por isso, usamos **Pygbag**: ele empacota o jogo para executar
Python/Pygame no próprio navegador, com WebAssembly. Não é necessário um
backend para o modo solo. As salas de amigos usam o servidor descrito acima.
[Documentação do Pygbag](https://pygame-web.github.io/wiki/pygbag/).

Instale a ferramenta de exportação e gere o site:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-web.txt
.\.venv\Scripts\python.exe exportar_web.py
.\.venv\Scripts\python.exe -m http.server 8000 --directory jogo/build/web
```

Abra **http://localhost:8000**. Use `Ctrl+C` para encerrar o servidor.
Os arquivos prontos ficam em **`jogo/build/web`**. Não abra `index.html`
diretamente pelo explorador de arquivos; o carregamento precisa de HTTP.

Se aparecer apenas o fundo azul, gere a exportação novamente com
`exportar_web.py` e recarregue com **Ctrl+Shift+R**. O carregador está
configurado para buscar o Pygame no CDN oficial também em `localhost`,
sem depender de um proxy local em `/cdn/`. O aviso de carregamento só
desaparece depois que o jogo desenha a primeira tela.

Ao editar o jogo, execute `exportar_web.py` novamente e recarregue a página.
O primeiro carregamento pode demorar porque baixa o Python e o Pygame.
A exportação usa os arquivos de execução do CDN oficial do Pygbag, portanto
a versão web precisa de acesso à internet. A versão de computador funciona
sem internet depois de instalar as dependências.

No celular, a resolução considera `devicePixelRatio`, a densidade de pixels
da tela. Por exemplo, um jogo exibido em 390 × 844 numa tela 3x é desenhado
em 1170 × 2532 pixels. Ao girar o aparelho, o tamanho e os toques são
recalculados. Depois de atualizar o código, gere a exportação e publique
os arquivos novamente; recarregue a página no celular para ver a nova versão.

### Publicar gratuitamente no Render

O Render oferece **Static Sites** gratuitos, sujeitos às cotas de uso da
plataforma. Este projeto inclui um `render.yaml` com a configuração do site.
[Documentação de sites estáticos](https://render.com/docs/static-sites) e
[limites do plano gratuito](https://render.com/docs/free).

1. Envie este projeto para um repositório no GitHub, GitLab ou Bitbucket.
   Inclua `jogo/assets`, `web`, os arquivos Python e os requirements.
   A pasta `.venv` e os arquivos gerados em `build` ficam fora do Git.
2. No Render, selecione **New → Static Site** e conecte o repositório.
3. Preencha:

   | Campo | Valor |
   | --- | --- |
   | Build Command | `pip install -r requirements-web.txt && python exportar_web.py` |
   | Publish Directory | `jogo/build/web` |

4. Crie o site e aguarde a construção. O Render fornece um endereço público
   para compartilhar com outras pessoas.

Também é possível usar **New → Blueprint** para o Render ler o `render.yaml`.
A versão de Python do build está indicada em `.python-version`.
[Referência do Blueprint](https://render.com/docs/blueprint-spec).

O projeto está preparado para publicação; a criação do site na sua conta
Render e o endereço público dependem desses passos. O `render.yaml` publica
o site estático; o servidor de salas deve ser hospedado separadamente para
disputas pela internet.

## Verificar as regras

Sem instalar nenhuma ferramenta extra:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes cobrem regras solo, timeout, dicas, lobby, autorização de anfitrião,
respostas concorrentes, pontos ocultos até o encerramento, posição fora do
top 5, empates, ícones, atualização do catálogo, troca de anfitrião e uma partida
completa pelas telas até o pódio. A integração HTTP usa dois clientes reais e portas
temporárias locais. As telas são testadas sem abrir uma janela visível.
Os testes de áudio carregam o OGG real usando uma saída de áudio simulada,
verificam ligar/desligar e a continuidade do jogo sem um dispositivo de som.
Também há verificações de JSON inesperado e timeout no cliente HTTP, índices
inválidos de pergunta e seleção de tema por clique, toque e teclado.
