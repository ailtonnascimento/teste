# Tutorial introdutório: Milestone MIP SDK

Este tutorial foi criado para orientar os primeiros estudos sobre o **Milestone Integration Platform Software Development Kit (MIP SDK)**, usado para integrar soluções ao **Milestone XProtect**, uma plataforma de VMS (Video Management Software) para gerenciamento de vídeo, eventos, alarmes, dispositivos e operadores.

> Escopo: visão geral, conceitos essenciais, preparação do ambiente, primeiro teste via API, primeiro caminho em C#/.NET e roteiro de estudo.

---

## 1. O que é o MIP SDK?

O **MIP SDK** é o conjunto de bibliotecas, APIs, documentação, modelos de projeto, ferramentas e exemplos fornecido pela Milestone para criar integrações com o XProtect. Com ele, um desenvolvedor pode:

- Ler configuração do VMS, como sites, câmeras, usuários, eventos e regras.
- Consumir vídeo ao vivo, vídeo gravado, áudio e metadados.
- Disparar eventos e alarmes para acionar regras no XProtect.
- Enviar comandos de controle, por exemplo PTZ, saída externa, bookmark ou start/stop de gravação.
- Criar aplicações independentes em C#.
- Criar plug-ins que rodam dentro do Smart Client, Management Client ou Event Server.
- Integrar por protocolos de rede, como REST, WebSocket, GraphQL, SOAP ou TCP, quando a solução não precisa ser um plug-in nativo.

Em termos simples: o MIP SDK é a porta de entrada para transformar o XProtect em uma plataforma extensível, conectada a sistemas externos e adaptada a fluxos de operação específicos.

---

## 2. Onde o MIP SDK se encaixa no XProtect?

Uma implantação típica do XProtect envolve vários componentes:

- **Management Server**: concentra configuração, usuários, permissões e estado lógico do sistema.
- **Recording Server**: recebe, grava e fornece vídeo de câmeras e outros dispositivos.
- **Event Server**: processa eventos, alarmes, mapas, integrações e comunicação MIP.
- **Smart Client**: aplicação usada por operadores para monitorar vídeo, alarmes e incidentes.
- **Management Client**: aplicação administrativa usada para configurar o sistema.
- **API Gateway**: ponto de entrada para APIs modernas, como REST e WebSocket.
- **Identity Provider (IDP)**: serviço usado para autenticação e emissão de tokens.

O MIP SDK conversa com esses componentes de formas diferentes, dependendo do tipo de integração escolhido.

---

## 3. Os três modos de integração

A documentação oficial organiza o MIP SDK em três grandes modos: **Protocol**, **Component** e **Plug-in**.

### 3.1 Protocol Integration

Use **Protocol Integration** quando sua aplicação deve conversar com o XProtect por APIs de rede. É a melhor opção para serviços backend, integrações web, automações, aplicações em linguagens que não sejam C# ou cenários em que você quer evitar instalar DLLs do MIP SDK no processo da aplicação.

Exemplos de uso:

- Um serviço Python ou Node.js que consulta alarmes.
- Um backend que dispara eventos de analytics.
- Uma aplicação web que lista câmeras e sites.
- Um sistema corporativo que integra regras do XProtect via REST.

APIs e áreas comuns:

- Configuration API
- Events API
- Alarms API
- Bookmarks API
- Evidence Locks API
- Messaging
- Control
- Video, Audio & Metadata
- Authentication
- Status

### 3.2 Component Integration

Use **Component Integration** quando você está criando uma aplicação independente em C#/.NET, mas quer usar os componentes e bibliotecas nativas do MIP SDK.

Exemplos de uso:

- Uma aplicação desktop que mostra vídeo ao vivo de câmeras do XProtect.
- Um painel operacional customizado.
- Uma aplicação que autentica no XProtect e acessa configuração.
- Um serviço local que dispara eventos e comandos.

Recursos típicos:

- Exibir vídeo ao vivo e gravado.
- Obter streams de vídeo.
- Acessar configuração do sistema.
- Enviar eventos.
- Emitir comandos de controle.
- Usar telas e componentes auxiliares de login.

### 3.3 Plug-in Integration

Use **Plug-in Integration** quando a solução precisa rodar dentro de uma aplicação XProtect, como o Smart Client, Management Client ou Event Server.

Exemplos de uso:

- Adicionar uma aba customizada ao Smart Client.
- Sobrepor gráficos em vídeo ao vivo ou gravado.
- Criar ações customizadas de regra no Event Server.
- Receber eventos em tempo real.
- Criar uma página de configuração no Management Client.
- Compartilhar configurações entre plug-ins e aplicações.

Esse modo é poderoso, mas exige maior cuidado com ciclo de vida, instalação, compatibilidade de versão, carregamento de DLLs e logs do host.

---

## 4. Como escolher o modo correto?

| Necessidade | Modo recomendado |
| --- | --- |
| Chamar APIs por HTTP a partir de qualquer linguagem | Protocol |
| Criar backend, automação ou integração cloud/on-premise | Protocol |
| Criar aplicação desktop C# independente | Component |
| Mostrar vídeo usando componentes nativos do SDK | Component |
| Alterar a experiência do operador no Smart Client | Plug-in |
| Criar ações, itens ou processamento dentro do Event Server | Plug-in |
| Criar telas administrativas no Management Client | Plug-in |

Regra prática:

- Comece por **Protocol** se seu objetivo é aprender com menor atrito.
- Vá para **Component** quando precisar de recursos nativos .NET, principalmente vídeo e componentes prontos.
- Use **Plug-in** quando a integração precisa aparecer ou executar dentro do ecossistema XProtect.

---

## 5. Pré-requisitos para estudar

Para seguir os estudos com prática, prepare:

1. **Conta Milestone**
   - Necessária para downloads, licenças e acesso a recursos de parceiro.

2. **Ambiente XProtect de desenvolvimento**
   - A documentação oficial recomenda um sistema separado e pequeno para desenvolvimento.
   - Para as APIs modernas, use XProtect VMS 2022 R1 ou posterior.

3. **Licença**
   - Você pode usar licença de avaliação ou licença de desenvolvimento/parceiro, conforme disponibilidade.

4. **Windows para desenvolvimento C#**
   - Visual Studio.
   - Templates do MIP SDK, quando usar plug-ins ou projetos C#.
   - Pacotes NuGet da Milestone, como `MilestoneSystems.VideoOS.Platform.SDK`.

5. **Ferramentas para APIs**
   - Postman, curl, PowerShell ou similar.
   - Conhecimento básico de HTTP, JSON e OAuth/Bearer tokens.

6. **Certificados**
   - Para produção, use HTTPS com certificado válido.
   - Evite HTTP em ambientes reais, pois credenciais e tokens podem trafegar em texto claro.

---

## 6. Primeiro exercício: testar a API Gateway

Este é o caminho mais simples para começar, porque você pode validar a comunicação sem escrever uma aplicação completa.

### 6.1 Verificar se a API Gateway responde

Substitua `xprotect.example.com` pelo host do seu ambiente:

```bash
curl --insecure --request GET "https://xprotect.example.com/api/.well-known/uris"
```

Se o ambiente foi instalado sem HTTPS, use `http://`, mas trate isso apenas como laboratório.

### 6.2 Obter um token

Exemplo com usuário básico:

```bash
curl --insecure --request POST "https://xprotect.example.com/API/IDP/connect/token" \
  --header "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "grant_type=password" \
  --data-urlencode "username=seu_usuario" \
  --data-urlencode "password=sua_senha" \
  --data-urlencode "client_id=GrantValidatorClient"
```

A resposta deve conter algo parecido com:

```json
{
  "access_token": "eyJ...",
  "expires_in": 3600,
  "token_type": "Bearer",
  "scope": "managementserver"
}
```

Guarde o `access_token` apenas temporariamente. Não salve tokens em código-fonte.

### 6.3 Fazer a primeira chamada REST

```bash
curl --insecure --request GET "https://xprotect.example.com/api/rest/v1/sites" \
  --header "Authorization: Bearer SEU_TOKEN"
```

Se a chamada retornar uma lista de sites, você validou:

- conectividade com o host;
- funcionamento da API Gateway;
- autenticação no IDP;
- autorização básica para consultar configuração.

---

## 7. Segundo exercício: explorar eventos e alarmes

Depois de listar sites, experimente áreas funcionais:

```bash
curl --insecure --request GET "https://xprotect.example.com/api/rest/v1/events" \
  --header "Authorization: Bearer SEU_TOKEN"
```

```bash
curl --insecure --request GET "https://xprotect.example.com/api/rest/v1/alarms" \
  --header "Authorization: Bearer SEU_TOKEN"
```

Ideias de estudo:

- Liste tipos de eventos disponíveis.
- Entenda a diferença entre eventos, regras e alarmes.
- Crie uma regra no Management Client e veja como um evento pode acioná-la.
- Verifique permissões do usuário quando uma chamada retornar 401 ou 403.

---

## 8. Primeiro caminho em C# com Component Integration

Quando você quiser sair das chamadas REST e usar bibliotecas nativas, crie uma aplicação C# e adicione os pacotes NuGet do MIP SDK. Para aplicações independentes, o pacote central costuma ser:

```bash
dotnet add package MilestoneSystems.VideoOS.Platform.SDK
```

> Observação: confirme a versão compatível com a versão do seu XProtect e com o tipo de projeto usado. Em projetos MIP, compatibilidade de versão importa.

Um fluxo conceitual de login em aplicação independente é:

1. Inicializar o ambiente SDK.
2. Informar o endereço do Management Server.
3. Criar credenciais.
4. Adicionar o servidor ao ambiente.
5. Realizar login.
6. Consultar configuração ou usar componentes de vídeo/eventos.

Exemplo simplificado baseado no padrão documentado:

```csharp
using System;
using System.Net;
using VideoOS.Platform.Login;
using VideoOS.Platform.SDK;

class Program
{
    static void Main()
    {
        Environment.Initialize();

        var managementServerUri = new Uri("https://xprotect.example.com");
        var secureOnly = true;
        var masterOnly = true;

        var integrationId = new Guid("7A7B4B62-A6F1-49E4-9C61-D541CC54411A");
        var integrationName = "MeuPrimeiroEstudoMIP";
        var version = "1.0.0.0";
        var manufacturerName = "MinhaEmpresa";

        CredentialCache credentials =
            Util.BuildCredentialCache(
                managementServerUri,
                "seu_usuario",
                "sua_senha",
                "Basic");

        Environment.AddServer(
            secureOnly,
            managementServerUri,
            credentials,
            masterOnly);

        Environment.Login(
            managementServerUri,
            integrationId,
            integrationName,
            version,
            manufacturerName,
            masterOnly);

        Console.WriteLine("Login realizado com sucesso.");
    }
}
```

Esse exemplo é apenas o começo. Depois do login, estude como navegar pela configuração, localizar câmeras, consumir vídeo e enviar eventos.

---

## 9. Primeiro caminho com Plug-in Integration

Para plug-ins, o fluxo de estudo recomendado é:

1. Instale os templates oficiais do MIP SDK para Visual Studio.
2. Crie um projeto a partir de um template, por exemplo:
   - plug-in genérico;
   - plug-in para Smart Client;
   - plug-in de Search;
   - plug-in de Access Control;
   - driver MIP, se o caso for integração de dispositivo.
3. Compile o projeto.
4. Copie as DLLs para a pasta `MIPPlugins` do host correspondente.
5. Reinicie o Smart Client, Management Client ou Event Server.
6. Verifique se o plug-in foi carregado.
7. Depure anexando o Visual Studio ao processo do host.

Pastas comuns:

- Smart Client: `%PROGRAMFILES%\Milestone\XProtect Smart Client\MIPPlugins\`
- Management Client: `%PROGRAMFILES%\Milestone\XProtect Management Client\MIPPlugins\`
- Event Server: `%PROGRAMFILES%\Milestone\XProtect Event Server\MIPPlugins\`

Em plug-ins, preste atenção ao tipo de ambiente declarado, por exemplo `Client`, `SmartClient`, `Administration`, `Service` ou `Standalone`, conforme o caso.

---

## 10. Conceitos que você deve dominar

### Autenticação e autorização

Aprenda a diferença entre:

- usuário básico do XProtect;
- usuário Windows/AD;
- token OAuth/Bearer;
- permissões no Management Client;
- autenticação para REST versus autenticação em componentes .NET.

### FQID

O **FQID** identifica itens dentro do ecossistema MIP. Ele aparece em câmeras, servidores, dispositivos, plug-ins, endpoints e mensagens. Entender FQID ajuda a navegar configuração, mensagens e eventos.

### Eventos, regras e alarmes

- **Evento**: algo aconteceu, por exemplo movimento, analytics, entrada externa ou evento customizado.
- **Regra**: lógica configurada no XProtect para reagir a eventos.
- **Alarme**: ocorrência operacional que exige atenção do operador.

### Ambientes MIP

O mesmo código conceitual pode rodar em contextos diferentes:

- Standalone
- Smart Client
- Management Client
- Event Server
- Service

Cada ambiente tem ciclo de vida, permissões e APIs disponíveis diferentes.

### Versionamento

Sempre confira:

- versão do XProtect;
- versão dos pacotes NuGet;
- versão dos templates;
- arquitetura x64;
- dependências copiadas junto com o plug-in;
- notas de release do MIP SDK.

---

## 11. Roteiro de estudo sugerido

### Etapa 1: Fundamentos do XProtect

- Entenda Management Server, Recording Server, Event Server, Smart Client e Management Client.
- Instale ou acesse um laboratório.
- Crie usuários, câmeras simuladas ou dispositivos de teste.

### Etapa 2: Protocol Integration

- Teste `/api/.well-known/uris`.
- Obtenha token no IDP.
- Consulte `/api/rest/v1/sites`.
- Explore Configuration, Events e Alarms APIs.
- Automatize uma chamada simples em Python, PowerShell ou Node.js.

### Etapa 3: Component Integration

- Crie aplicação C# independente.
- Instale `MilestoneSystems.VideoOS.Platform.SDK`.
- Faça login via SDK.
- Liste itens de configuração.
- Abra vídeo ao vivo de uma câmera usando samples oficiais como referência.

### Etapa 4: Plug-in Integration

- Instale templates do Visual Studio.
- Compile um sample.
- Carregue no Smart Client.
- Adicione uma aba simples.
- Leia logs do host e pratique depuração.

### Etapa 5: Projeto prático

Construa uma prova de conceito pequena:

- Um serviço recebe um alerta de um sistema externo.
- O serviço dispara um evento no XProtect via REST.
- Uma regra no XProtect transforma esse evento em alarme.
- O operador visualiza o alarme no Smart Client.

Esse projeto conecta os conceitos de autenticação, eventos, regras, alarmes e operação.

---

## 12. Erros comuns de iniciantes

- Usar HTTP em ambiente real.
- Esquecer que o usuário precisa de permissões no XProtect.
- Misturar versões incompatíveis de SDK, NuGet e XProtect.
- Não reiniciar o host depois de instalar um plug-in.
- Copiar apenas a DLL principal e esquecer dependências.
- Não consultar logs do Event Server ou Smart Client.
- Tratar evento, regra e alarme como a mesma coisa.
- Começar por plug-in complexo antes de validar chamadas REST simples.
- Salvar usuário, senha ou token no código.

---

## 13. Checklist para seu primeiro laboratório

- [ ] Tenho acesso a um XProtect de teste.
- [ ] Sei o endereço do Management Server/API Gateway.
- [ ] Tenho usuário com permissões adequadas.
- [ ] Consigo acessar `/api/.well-known/uris`.
- [ ] Consigo obter token no IDP.
- [ ] Consigo chamar `/api/rest/v1/sites`.
- [ ] Li a página oficial sobre Protocol, Component e Plug-in.
- [ ] Baixei ou clonei samples oficiais.
- [ ] Instalei Visual Studio e templates se for estudar C#.
- [ ] Documentei versões usadas no laboratório.

---

## 14. Referências oficiais para continuar

- Documentação MIP SDK: https://doc.developer.milestonesys.com/
- Protocol, Component ou Plug-in: https://doc.developer.milestonesys.com/mipvmsapi/content/integration-modes/
- Quickstart MIP SDK/API Gateway: https://doc.developer.milestonesys.com/mipvmsapi/content/quickstart/
- APIs de protocolo: https://doc.developer.milestonesys.com/mipvmsapi/api-overview/
- Getting Started Guide em PDF: https://doc.milestonesys.com/sysarch/pdf/latest/en-US/MilestoneMIPSDK_GettingStartedGuide_en-US.pdf
- Samples oficiais de Component Integration: https://github.com/milestonesys/mipsdk-samples-component
- Templates do MIP SDK para Visual Studio: https://marketplace.visualstudio.com/items?itemName=milestonesys.mipsdk-templates
- Pacote NuGet `MilestoneSystems.VideoOS.Platform.SDK`: https://www.nuget.org/packages/MilestoneSystems.VideoOS.Platform.SDK/

---

## 15. Próximos passos

Para iniciar de forma segura:

1. Leia a página oficial sobre os três modos de integração.
2. Faça o exercício da API Gateway.
3. Consulte os samples oficiais.
4. Escolha um problema simples do seu contexto.
5. Implemente primeiro por REST.
6. Só depois avance para Component ou Plug-in se houver necessidade real.

Com essa base, você terá uma visão clara de quando usar cada parte do MIP SDK e como evoluir de chamadas simples para integrações completas no ecossistema Milestone XProtect.
