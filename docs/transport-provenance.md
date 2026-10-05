# Origem do trabalho

O transporte foi escrito do zero em Python para substituir o uso de uma
biblioteca ARM proprietária em uma integração particular de Home Assistant.
Não há código-fonte do fornecedor, binário redistribuído, mecanismo de
`ctypes`/`dlopen`, chamada a QEMU ou dependência do SDK neste pacote.

O processo de pesquisa incluiu a leitura do wrapper existente, a inspeção dos
símbolos e instruções do ELF privado e testes de interoperabilidade com o
gravador do proprietário do projeto. Por isso, este trabalho **não é clean
room**. Escrever código novo e separá-lo do SDK não resolve por si só a análise
contratual e de propriedade intelectual necessária à publicação.

O TEA foi implementado a partir da definição matemática do algoritmo padrão,
com teste de vetor conhecido. Seu uso aqui reproduz um formato legado. Na
descoberta e no registro, a chave do TEA é o próprio cabeçalho transmitido, logo
esse ciframento não fornece confidencialidade contra alguém que observe o
tráfego.

Os testes distribuídos usam identidades fictícias, `*.example` e endereços de
documentação `192.0.2.0/24`. Não contêm credenciais reais, seriais, endereços
públicos do proprietário, imagens ou bytes capturados de sua câmera.

As disassemblies, capturas, biblioteca proprietária e histórico privado anterior
não fazem parte do repositório público. O histórico público começa com o código
Python e parâmetros fictícios nos testes.

A licença MIT cobre o código novo desta pasta. Ela não concede direitos sobre
chaves do fornecedor, SDK, firmware, marcas ou disponibilidade do serviço
cloud. O pacote recebe os parâmetros de serviço pela aplicação usuária.
