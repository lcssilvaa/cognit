"""Perguntas de UX e Design: usabilidade, protótipos, Figma e acessibilidade.

Mesma estrutura de perguntas.py: dificuldade, enunciado, alternativas,
correta (índice a partir de zero), dica e explicação. Usadas nos dois modos.
"""

PERGUNTAS_UX_DESIGN = [
    # https://www.nngroup.com/articles/usability-101-introduction-to-usability/
    {
        "dificuldade": "Iniciante",
        "enunciado": "O que uma boa usabilidade busca facilitar em um aplicativo?",
        "alternativas": [
            "A quantidade de efeitos visuais",
            "A realização das tarefas do usuário",
            "O número de telas do aplicativo",
            "A troca frequente dos botões de lugar",
        ],
        "correta": 1,
        "dica": "Pense em alguém tentando concluir uma tarefa com clareza e poucos erros.",
        "explicacao": "Usabilidade considera a facilidade de aprender e usar uma interface para realizar tarefas, com eficiência e poucos erros.",
    },
    # https://www.figma.com/resource-library/what-is-wireframing/
    {
        "dificuldade": "Básico",
        "enunciado": "Qual é o principal objetivo de um wireframe de baixa fidelidade?",
        "alternativas": [
            "Definir todas as animações finais",
            "Publicar o aplicativo na loja",
            "Planejar a estrutura e o conteúdo",
            "Implementar o banco de dados",
        ],
        "correta": 2,
        "dica": "É um esboço que organiza os elementos antes do acabamento visual.",
        "explicacao": "Um wireframe de baixa fidelidade ajuda a discutir a organização da tela e dos conteúdos sem exigir cores e detalhes finais.",
    },
    # https://help.figma.com/hc/en-us/articles/360040314193-Guide-to-prototyping-in-Figma
    {
        "dificuldade": "Intermediário",
        "enunciado": "Para que serve um protótipo navegável antes de programar o aplicativo?",
        "alternativas": [
            "Simular e avaliar fluxos de interação",
            "Garantir que não haverá nenhum erro",
            "Substituir toda pesquisa com usuários",
            "Gerar automaticamente o sistema final",
        ],
        "correta": 0,
        "dica": "Ele permite experimentar o caminho entre telas sem ter o produto completo.",
        "explicacao": "O protótipo simula comportamentos e navegação. Isso permite avaliar ideias e encontrar problemas antes de implementar o produto.",
    },
    # https://www.nngroup.com/articles/usability-testing-101/
    {
        "dificuldade": "Intermediário II",
        "enunciado": "Em um teste de usabilidade, qual conduta ajuda a encontrar dificuldades reais?",
        "alternativas": [
            "Ensinar cada clique ao participante",
            "Perguntar apenas se a tela é bonita",
            "Corrigir todo erro imediatamente",
            "Observar tarefas sem indicar o caminho",
        ],
        "correta": 3,
        "dica": "A ajuda constante pode esconder um problema da interface.",
        "explicacao": "Tarefas realistas e observação sem conduzir os cliques ajudam a identificar onde as pessoas têm dúvidas ou não conseguem avançar.",
    },
    # https://help.figma.com/hc/en-us/articles/360039823894-Create-and-manage-prototype-flows
    {
        "dificuldade": "Avançado",
        "enunciado": "No Figma, como simular um botão que abre outra tela no protótipo?",
        "alternativas": [
            "Exportar o botão como imagem PNG",
            "Conectar o botão ao frame de destino",
            "Mudar somente a cor do texto",
            "Renomear a camada do botão",
        ],
        "correta": 1,
        "dica": "Uma interação precisa de um gatilho e de um destino.",
        "explicacao": "Uma conexão de protótipo pode ligar o botão ao frame de destino, usando um gatilho de clique/toque e uma ação de navegação.",
    },
    # https://help.figma.com/hc/en-us/articles/360040451373-Guide-to-auto-layout-in-Figma
    {
        "dificuldade": "Desafio I",
        "enunciado": "Um botão no Figma deve se ajustar a textos maiores. Como o Auto Layout pode ajudar?",
        "alternativas": [
            "Convertendo o botão em uma foto",
            "Impedindo mudanças no conteúdo",
            "Organizando conteúdo e espaçamentos",
            "Substituindo o texto por um ícone",
        ],
        "correta": 2,
        "dica": "Pense no espaço interno ao redor do texto e no ajuste ao conteúdo.",
        "explicacao": "O Auto Layout organiza elementos e espaçamentos. Com dimensionamento ajustado ao conteúdo, o botão pode acompanhar mudanças no texto.",
    },
    # https://help.figma.com/hc/en-us/articles/360038662654-Guide-to-components-in-Figma
    {
        "dificuldade": "Desafio II",
        "enunciado": "Qual vantagem existe em usar instâncias de um componente de botão no Figma?",
        "alternativas": [
            "Reutilizar padrões e propagar mudanças",
            "Impedir qualquer variação de texto",
            "Criar um arquivo novo a cada botão",
            "Eliminar a necessidade de testar",
        ],
        "correta": 0,
        "dica": "As instâncias mantêm uma ligação com o componente principal.",
        "explicacao": "Instâncias permitem reutilizar o componente e receber atualizações do principal. Personalizações locais podem alterar o que uma instância herda.",
    },
    # https://www.w3.org/WAI/tutorials/forms/labels/
    {
        "dificuldade": "Desafio III",
        "enunciado": "Qual solução ajuda a tornar um campo de formulário mais acessível?",
        "alternativas": [
            "Usar somente um placeholder que some",
            "Identificar o campo apenas pela cor",
            "Usar um rótulo claro associado ao campo",
            "Esconder o nome do campo de todos",
        ],
        "correta": 2,
        "dica": "A pessoa precisa saber o que preencher, inclusive usando leitor de tela.",
        "explicacao": "Um rótulo claro, corretamente associado ao campo, ajuda a identificar sua finalidade. O placeholder sozinho não substitui esse rótulo.",
    },
    # https://www.w3.org/WAI/WCAG21/Techniques/general/G177
    {
        "dificuldade": "Desafio IV",
        "enunciado": "Um usuário digitou um e-mail inválido. Qual feedback ajuda mais a corrigir o erro?",
        "alternativas": [
            "Apagar todos os campos preenchidos",
            "Mostrar apenas uma borda vermelha",
            "Exibir somente a mensagem 'Erro 42'",
            "Explicar o problema e como corrigi-lo",
        ],
        "correta": 3,
        "dica": "A mensagem deve orientar a próxima ação, sem perder os dados já digitados.",
        "explicacao": "Um feedback útil identifica o campo e o problema, sugere uma correção conhecida e preserva os dados para facilitar a nova tentativa.",
    },
    # https://www.nngroup.com/articles/usability-101-introduction-to-usability/
    {
        "dificuldade": "Desafio final",
        "enunciado": "Um teste revelou dificuldade para finalizar uma compra. Qual é o próximo passo mais adequado?",
        "alternativas": [
            "Ignorar os resultados e publicar",
            "Revisar o fluxo e testar novamente",
            "Trocar só as cores e encerrar o estudo",
            "Concluir que todo usuário já aprendeu",
        ],
        "correta": 1,
        "dica": "O design evolui por ciclos de observação, ajuste e nova avaliação.",
        "explicacao": "Use as dificuldades observadas para revisar o fluxo e avaliar a nova versão. A iteração ajuda a verificar se as mudanças resolveram o problema.",
    },
]
