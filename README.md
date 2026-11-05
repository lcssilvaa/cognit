# Cognit

Quiz de tecnologia feito em **Python com Pygame**, seguindo as cores, os
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
- São **5 perguntas**, em ordem de dificuldade: Iniciante, Básico,
  Intermediário, Avançado e Desafio.
- Cada acerto aumenta o progresso em 20% e libera a próxima pergunta.
- Cada erro desconta uma vida. A pergunta se mantém e a alternativa errada
  fica desativada; escolha outra para continuar.
- Ao acertar todas, você vence. Ao perder a terceira vida, a partida acaba.
- As telas de acerto explicam a resposta. Reiniciar recupera as três vidas.

Clique/toque nos botões ou use **Tab/setas** para navegar e **Enter/espaço**
para confirmar. Nas perguntas, **A/B/C/D** ou **1/2/3/4** selecionam as opções.
**Esc** permite sair da pergunta com confirmação. A janela pode ser
redimensionada e mantém a proporção do protótipo.

Tecnologia é o único tema disponível. Os outros aparecem como “Em breve”.
Criar quizzes pela interface, login, ranking e salvamento entre sessões
ficam fora desta primeira versão.

## Onde personalizar

| Arquivo | O que mudar |
| --- | --- |
| `jogo/perguntas.py` | Perguntas, alternativas, resposta correta, dificuldade e explicação |
| `jogo/config.py` | Nome, quantidade de vidas, cores e medidas |
| `jogo/partida.py` | Regras de acerto, erro, progresso, vitória e derrota |
| `jogo/main.py` | Organização de cada tela, navegação e eventos |
| `jogo/interface.py` | Aparência dos botões, cartões, texto e corações |
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

As posições e os tamanhos no código continuam seguindo o protótipo de
390 × 844. `Interface` converte essas medidas para os pixels reais da tela.
As fontes e os SVGs são desenhados diretamente nessa resolução, evitando
ampliar uma imagem pequena e desfocar a interface em celulares.

## Como explicar o código na apresentação

1. `main.py` abre a janela e executa o loop do jogo.
2. Cada quadro lê os eventos do mouse, toque ou teclado.
3. A ação selecionada chama uma regra de `Partida`, que guarda as vidas,
   os acertos e a pergunta atual.
4. O jogo escolhe uma tela e desenha seus elementos com `Interface`.
5. O desenho é ajustado ao tamanho da janela e exibido.

`Partida` não depende do Pygame: as regras podem ser lidas e testadas
separadamente dos desenhos. O `await asyncio.sleep(0)` no loop principal
cede a execução ao navegador e permite usar o mesmo jogo na versão web.

## Jogar no navegador

Uma janela Pygame aberta em um servidor não aparece no navegador de quem
acessa o site. Por isso, usamos **Pygbag**: ele empacota o jogo para executar
Python/Pygame no próprio navegador, com WebAssembly. Não é necessário um
backend para este quiz. [Documentação do Pygbag](https://pygame-web.github.io/wiki/pygbag/).

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
Render e o endereço público dependem desses passos. Cada pessoa joga sua
própria partida; esta versão não possui multiplayer nem ranking compartilhado.

## Verificar as regras

Sem instalar nenhuma ferramenta extra:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Os testes cobrem a vitória com cinco acertos, perda das três vidas,
tentativas repetidas, reinício e personalização de perguntas e vidas.
