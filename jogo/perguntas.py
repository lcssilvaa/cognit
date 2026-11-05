"""As perguntas aparecem nesta ordem: da mais fácil à mais difícil.

Para editar, altere os textos abaixo. A resposta correta usa a posição da lista:
0 = A, 1 = B, 2 = C, 3 = D. O campo codigo é opcional.
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
    # Nível 6 — API: consulta de informações.
    # Fonte: https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3.1
    {
        "dificuldade": "Desafio I",
        "enunciado": "Qual método HTTP é usado para consultar uma lista de produtos em uma API, sem alterá-los?",
        "alternativas": [
            "POST",
            "GET",
            "DELETE",
            "PATCH",
        ],
        "correta": 1,
        "explicacao": "GET consulta informações de um recurso. POST envia dados para processamento, DELETE remove e PATCH aplica alterações parciais.",
    },
    # Nível 7 — Containers/Docker: imagem e container.
    # Fonte: https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/
    {
        "dificuldade": "Desafio II",
        "enunciado": "No Docker, qual é a relação entre uma imagem e um container?",
        "alternativas": [
            "A imagem só existe com o container ligado",
            "O container é o instalador do Docker",
            "A imagem é o modelo; o container é uma instância",
            "Imagem e container são sempre a mesma coisa",
        ],
        "correta": 2,
        "explicacao": "A imagem reúne a aplicação e suas dependências. A partir dela, o Docker cria containers para executar a aplicação de forma isolada.",
    },
    # Nível 8 — Cloud: crescimento de uma aplicação.
    # Fonte: https://learn.microsoft.com/en-us/azure/architecture/best-practices/auto-scaling
    {
        "dificuldade": "Desafio III",
        "enunciado": "O acesso a um site na cloud aumentou. O que significa escalar a aplicação horizontalmente?",
        "alternativas": [
            "Adicionar mais instâncias da aplicação",
            "Aumentar a RAM de uma única VM",
            "Aumentar o disco de uma única VM",
            "Mover o site para outra região",
        ],
        "correta": 0,
        "explicacao": "Escalar horizontalmente é adicionar instâncias para dividir a carga. Aumentar a capacidade de uma única máquina é escalar verticalmente.",
    },
    # Nível 9 — Protocolos: resolução de nomes.
    # Fonte: https://www.rfc-editor.org/rfc/rfc1034.html
    {
        "dificuldade": "Desafio IV",
        "enunciado": "Ao acessar um site, qual serviço permite descobrir o endereço IP associado ao nome exemplo.com?",
        "alternativas": [
            "HTTP",
            "FTP",
            "SSH",
            "DNS",
        ],
        "correta": 3,
        "explicacao": "O DNS associa nomes de domínio a registros, como endereços IP. Isso permite acessar um site pelo nome, sem memorizar seu IP.",
    },
    # Nível 10 — Protocolos: entrega ordenada e retransmissão.
    # Fonte: https://www.rfc-editor.org/rfc/rfc9293.html
    {
        "dificuldade": "Desafio final",
        "enunciado": "Um sistema precisa receber dados em ordem e retransmitir os que se perderam. Qual protocolo de transporte é mais adequado?",
        "alternativas": [
            "DNS",
            "UDP",
            "TCP",
            "ICMP",
        ],
        "correta": 2,
        "explicacao": "O TCP oferece entrega ordenada e retransmissão de dados perdidos. O UDP, por si só, não oferece esses mecanismos.",
    },
]
