Os arquivos `marca.svg` e `mascote_*.svg` foram extraídos dos protótipos
originais da pasta `prototipo`, sem modificar os originais. O jogo usa os SVGs
e os desenha na resolução final da tela, para manter a nitidez no celular.
Os PNGs são alternativas para imagens que não tenham uma versão vetorial.

Para mudar o mascote, edite os três SVGs, preservando os nomes. Se preferir
usar PNGs, remova o SVG correspondente e substitua seu PNG, mantendo o nome
e a transparência do fundo. Use imagens com boa resolução: em uma tela 3x,
uma ilustração de 200 pixels do layout pode ocupar 600 pixels reais.

`Nunito.ttf` vem do projeto Nunito no repositório Google Fonts. As versões
`Nunito-Regular.ttf` e `Nunito-Bold.ttf` foram geradas dessa fonte com pesos
400 e 800, respectivamente, para manter a leitura consistente no Pygame:
https://github.com/google/fonts/tree/main/ofl/nunito

A licença da fonte está em `OFL-Nunito.txt`.

`musica_fundo.ogg` é uma composição instrumental original para o Cognit,
sintetizada por `scripts/gerar_musica.py`: 20 segundos, 96 BPM, mono a 24 kHz.
O gerador usa notas, acordes e envelopes definidos no próprio código, sem
gravações ou trechos de músicas de terceiros. O OGG é compartilhado pelas
versões desktop e web. Para personalizar, edite o gerador ou substitua esse
arquivo, mantendo o nome; o volume fica em `VOLUME_MUSICA` no `config.py`.
