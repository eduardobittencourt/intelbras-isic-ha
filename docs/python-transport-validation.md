# Validação do transporte próprio

Testes realizados em 5 de outubro de 2026, usando o gravador que já estava
configurado no Home Assistant do proprietário. O novo transporte e o adapter
da integração rodaram em `workspace`, no ambiente de desenvolvimento. A
instalação existente do HA não foi substituída.

## Resultados observados

- Descoberta de 27 servidores e validação do registro da aplicação no cloud.
- Negociação P2P direta IPv4 com o gravador real.
- Resposta RTSP pelo túnel próprio e autenticação com a conta do gravador.
- Decodificação H.264 de 704 × 480: primeiro quadro em 5,36 segundos.
- Oito canais simultâneos: um quadro autenticado de cada canal, entre 5,23 e
  5,37 segundos após o início da conexão.
- Oito canais em teste prolongado: 239 quadros por canal, 1.912 no total,
  com 30 segundos de decodificação após abrir cada vídeo e aproximadamente
  35,7 segundos totais. A renovação do registro cloud também foi validada
  nessa sessão; não houve falha do transporte.
- Sessão prolongada: 273 quadros, por 35 segundos de decodificação após abrir
  o vídeo, em 40,25 segundos totais, sem falha do transporte.
- Integração de referência no HA: 243 quadros em 35,12 segundos totais.
- Testes sintéticos: retransmissão após perda, reordenação, duplicação,
  limites de buffer, mensagens malformadas e cliente RTSP silencioso enquanto
  continua recebendo mídia.
- Adapter assíncrono: início idempotente, recriação de worker morto,
  limpeza após erro e cancelamento durante a conexão.
- Adapter real da branch: oito canais autenticados com `DESCRIBE`, quadro
  H.264 de 704 × 480 decodificado e encerramento da sessão confirmado.
- Suítes locais aprovadas: 19 testes do transporte e 11 da integração;
  Ruff e verificação de formatação aprovados nos dois projetos.

Não foram gravadas imagens. As credenciais RTSP e o serial foram lidos da
configuração privada existente e usados somente em memória. As capturas e as
disassemblies de pesquisa ficam fora desta branch.

Uma falha de teste prolongado foi corrigida: o proxy não deve fechar o TCP
porque o cliente deixou de enviar comandos durante a reprodução. O teste de
regressão mantém mídia recebida depois do timeout de polling de envio.

## Alcance

Esta evidência demonstra a remoção funcional da dependência da biblioteca
proprietária para o equipamento e a rede testados. Não é certificação para
todos os modelos. IPv6, relay, outras arquiteturas, outros firmwares e sessões
de horas ainda precisam ser exercitados. A branch não foi instalada no HA.

Este relatório descreve os testes anteriores à publicação. Para a versão
pública, os parâmetros Cloud foram removidos do código e passaram a ser
informados na configuração privada do HA; os binários e o histórico anterior
foram mantidos em arquivo privado separado, e o ícone foi substituído por arte
original. A origem da implementação está em
[transport-provenance.md](transport-provenance.md).
