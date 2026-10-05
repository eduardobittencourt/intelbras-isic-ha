# Validação da release pelo HACS

Em 5 de outubro de 2026, a release pública `v0.3.1` foi instalada pelo instalador
do HACS na instância Home Assistant do proprietário do projeto. O gravador está
em outra rede; o acesso continuou usando o serviço Intelbras e o transporte P2P.
Não foram salvas imagens ou credenciais como artefatos de validação.

## Ambiente e instalação

- Home Assistant 2026.9.4; HACS 2.0.5.
- Repositório público acessível sem autenticação, com licença MIT.
- Cadastro como repositório personalizado, categoria Integration, seguido de
  download de `v0.3.1` pela API WebSocket do próprio HACS, a mesma utilizada
  pelo frontend. Não foi feita cópia manual do código novo para o HA.
- Os 22 arquivos da integração instalada conferiram com os hashes SHA-256 dos
  arquivos da release, sem arquivo ausente ou modificado.
- O instalador preservou os oito binários da pasta `bridge/` da instalação
  manual anterior. Essa pasta obsoleta foi removida após backup do HA.
- Checagem de configuração aprovada e Home Assistant Core reiniciado.
- HACS informa a release instalada e nenhuma atualização pendente.

## Migração

A entrada de configuração existente foi migrada da versão 1 para a versão 2.
A reautenticação recebeu as credenciais Cloud em memória, salvando-as somente
na configuração privada do HA. A entrada existente e os identificadores das
oito câmeras foram preservados, e a integração voltou ao estado carregado.

## Resultado funcional

| Verificação | Resultado |
| --- | --- |
| Câmeras existentes | 8 preservadas e disponíveis |
| Entidades habilitadas, incluindo sensores | 13 disponíveis |
| Snapshots via API de câmera do HA | 8 JPEGs válidos, 704×480 |
| Vídeo via API HLS do HA | 8 canais H.264, quadros decodificados em 704×480 |
| Diagnósticos baixados pela API do HA | Serial, senha do gravador, app_key e senha P2P ocultos |
| Túnel depois dos testes de mídia | Pronto, sem recriação da sessão |
| Recarga oficial da integração | Carregada, oito câmeras disponíveis e snapshot válido |
| Binários nativos na integração instalada | 0 |

Foram solicitados streams HLS por meio de `camera/stream`, lidas playlists e
decodificados quadros dos segmentos produzidos pelo próprio HA. Isso verifica
a cadeia HA → transporte Python → gravador remoto → HLS, além da existência das
entidades e da resposta RTSP de configuração. Os segmentos foram processados
somente em memória.

## Falha encontrada e corrigida

A instalação inicial de `v0.3.0` passou nos testes de snapshots e vídeo, mas a
recarga posterior entrou em `setup_retry`. O domínio de descoberta retornou
seis endereços IPv4: o primeiro escolhido pelo HA não respondeu, enquanto os
outros cinco responderam. O cliente tentava somente o primeiro endereço.

A release `v0.3.1` passou a tentar endereços distintos com tentativas limitadas.
Ela foi baixada pelo HACS, o Core foi reiniciado e os oito testes de snapshots
e os oito de vídeo foram repetidos com sucesso. A recarga oficial, pela API de
configuração do HA, também passou: a entrada voltou carregada, as 13 entidades
habilitadas ficaram disponíveis e um novo snapshot confirmou o acesso ao
gravador. Essa verificação levou aproximadamente seis segundos.

## Validação de código e publicação

- 44 testes automatizados aprovados, incluindo migração, reautenticação,
  reconfiguração, cancelamento, perda/reordenação de pacotes, redaction e
  fallback de descoberta após timeout ou resposta inválida.
- Ruff e formatação aprovados.
- GitHub Actions: Tests, Hassfest e HACS aprovados para o código da release.
- Arquivos e blobs do histórico público examinados sem ocorrência das
  credenciais reais verificadas, seriais ou binários ELF.
- O histórico anterior foi mantido em um repositório privado separado.
  O blob da biblioteca proprietária não é acessível anonimamente pelo
  repositório público.

Esta evidência cobre o equipamento e a rede testados. Relay, IPv6, outros
firmwares e sessões de horas continuam pendentes. Novas instalações precisam
fornecer os dois parâmetros Cloud separadamente; o HACS não os distribui.
