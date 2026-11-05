"""As perguntas aparecem nesta ordem: da mais fácil à mais difícil.

Para editar, altere os textos abaixo. A resposta correta usa a posição da lista:
0 = A, 1 = B, 2 = C. O campo codigo é opcional.
"""

PERGUNTAS = [
    {
        "dificuldade": "Iniciante",
        "enunciado": "Qual destes é um sistema operacional?",
        "alternativas": ["Chrome", "Android", "Excel", "Java"],
        "correta": 1,
        "explicacao": "O Android gerencia os recursos do aparelho e permite executar aplicativos.",
    },
    {
        "dificuldade": "Básico",
        "enunciado": "Qual componente guarda temporariamente os dados dos programas em execução?",
        "alternativas": ["SSD", "Processador (CPU)", "Memória RAM", "HD"],
        "correta": 2,
        "explicacao": "A RAM armazena dados em uso. Seu conteúdo é perdido ao desligar o computador.",
    },
    {
        "dificuldade": "Intermediário",
        "enunciado": "O que o HTTPS acrescenta à comunicação entre o navegador e um site?",
        "alternativas": [
            "Criptografia dos dados em trânsito",
            "Proteção contra qualquer golpe",
            "Uma conexão de internet mais rápida",
            "Envio de e-mail"
        ],
        "correta": 0,
        "explicacao": "O HTTPS usa TLS para proteger os dados em trânsito. Isso não garante que o site seja confiável.",
    },
    {
        "dificuldade": "Avançado",
        "enunciado": "Quais produtos esta consulta SQL retorna?",
        "codigo": "SELECT nome FROM produtos\nWHERE preco > 100;",
        "alternativas": [
            "Todos os produtos da tabela",
            "Os que custam mais de 100",
            "Os que custam exatamente 100",
            "Filtra apenas a coluna preços"
        ],
        "correta": 1,
        "explicacao": "WHERE filtra as linhas. O operador > seleciona preços estritamente maiores que 100.",
    },
    {
        "dificuldade": "Desafio",
        "enunciado": "Qual é a saída deste código Python?",
        "codigo": "nums = [1, 2, 3]\nprint(len(nums[1:]))",
        "alternativas": ["0", "1", "2", "3"],
        "correta": 2,
        "explicacao": "nums[1:] gera [2, 3], pois os índices começam em zero. Essa lista tem 2 elementos.",
    },
]
