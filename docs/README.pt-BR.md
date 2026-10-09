# Intelbras iSIC Cloud para Home Assistant

Integração open source para acessar canais de gravadores Intelbras em outra rede,
com descoberta pelo Cloud e transporte P2P escrito em Python. Cria uma entidade
`camera` por canal, com vídeo ao vivo, snapshots e entidades de diagnóstico.
Não instala DLL proprietária, SDK nativo, QEMU ou rootfs ARM.

Este é um projeto independente, sem afiliação, endosso ou suporte da Intelbras.
O código original usa licença MIT. O ícone oficial do iSIC Lite pertence à
Intelbras e não está coberto pela licença MIT; veja os
[avisos de terceiros](../THIRD_PARTY_NOTICES.md).

## Requisitos

- Home Assistant **2026.9.4 ou posterior**; HACS recomendado;
- dispositivo funcionando no iSIC Lite;
- serial, usuário/senha locais e porta RTSP do gravador;
- **chave da aplicação Cloud (`app_key`) e senha P2P**, fornecidas separadamente;
- internet com conectividade UDP que permita P2P direto entre HA e gravador.

**As credenciais Cloud não são distribuídas pelo projeto.** Não são o login da
Conta Intelbras nem a senha local do gravador. Ainda não existe um fluxo de login
que as obtenha automaticamente. Sem esses parâmetros, a integração pode ser
baixada pelo HACS, mas não consegue concluir a configuração do equipamento.
Veja [a pesquisa sobre credenciais](cloud-credentials.md).

## Instalação pelo HACS

[Abrir no HACS](https://my.home-assistant.io/redirect/hacs_repository/?owner=eduardobittencourt&repository=intelbras-isic-ha&category=integration)

1. Em **HACS → ⋮ → Repositórios personalizados**, adicione
   `https://github.com/eduardobittencourt/intelbras-isic-ha`, categoria **Integração**.
2. Procure **Intelbras iSIC Cloud**, escolha **Baixar** e a release mais recente.
3. Reinicie o Home Assistant.
4. Acesse **Configurações → Dispositivos e serviços → Adicionar integração**.
5. Procure **Intelbras iSIC Cloud** e informe a configuração do gravador e os
   dois parâmetros Cloud fornecidos separadamente.

A instalação é como **repositório personalizado do HACS**. O projeto ainda não
está no catálogo padrão. Para instalar manualmente, copie a pasta
`custom_components/intelbras_isic` da release para `/config/custom_components/`
e siga os passos a partir do reinício.

## Configuração e atualização

Informe serial, usuário/senha do gravador, número de canais (1–32), perfil de
vídeo, porta RTSP (normalmente 554), `app_key` e senha P2P. O substream H.264 é
recomendado para reprodução no navegador. A configuração testa o túnel e a
resposta RTSP autenticada do canal 1 antes de salvar.

A opção **Reconfigurar** permite atualizar os parâmetros. Ao migrar da versão
privada, a integração preserva os dispositivos e identificadores das entidades,
mas pede reautenticação para receber as credenciais Cloud antes embutidas.
Mantenha esses valores na sua configuração privada antes de atualizar.

O HACS pode preservar arquivos da instalação manual anterior. Após fazer
backup, remova a pasta antiga `/config/custom_components/intelbras_isic/bridge/`
se ela existir; preserve o novo arquivo `bridge.py`. Essa pasta contém o runtime
nativo anterior, que não é mais utilizado.

Credenciais ficam na entrada de configuração do HA e são removidas dos
diagnósticos. Não publique `.storage`, credenciais, seriais ou imagens.

## Compatibilidade

Foram testados P2P IPv4 direto e vídeo H.264 no gravador remoto de oito canais do
proprietário, inclusive nos oito canais simultaneamente. Outros modelos,
firmwares e redes ainda precisam de validação.

- Relay pela nuvem, negociação IPv6 e peers antigos sem VDT não estão implementados.
- Até oito conexões TCP simultâneas por gravador; snapshots e vídeos compartilham o limite.
- Canais são informados manualmente; o codec depende da configuração do equipamento.
- Recuperação automática de vídeos já em reprodução ainda precisa de trabalho.
- A disponibilidade e autenticação do Cloud Intelbras continuam sendo dependências.

Veja [solução de problemas](troubleshooting.md), [arquitetura](architecture.md),
[origem do transporte](transport-provenance.md) e [como contribuir](../CONTRIBUTING.md).
Veja também a [validação da instalação pelo HACS](hacs-install-validation.md).
