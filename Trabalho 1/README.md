# Trabalho 1 - Sistema Distribuido de Conversa

Produzido por Thierry Pierre, Jorge Oliveira, Luan Martins e Vinícius Lettiéri.

## Introdução

Nesse trabalho, almejamos criar uma aplicação de mensageria distribuída, com um servidor central que funciona como uma referência para os endereços dos demais usuários e a aplicação do lado dos usuários, que trabalham no esquema peer-to-peer, com comunicação direta entre eles.

## Estrutura do Sistema

O sistema é composto do lado do **servidor central**, que é responsável por **guardar a lista de usuários ativos** e **receber os logins e logoffs dos usuários**, e também do **lado dos usuários**, que se comunicam entre si.

Do **lado do usuário**, temos a seguinte organização:

- **Módulo Cliente**: Classe responsável por encapsular o lado cliente que comunica com o servidor central e os demais usuários. Permite o envio de mensagens e a recuperação da resposta.
- **Módulo Cordenador de Servidores:** Classe criada após o login ser realizado, abrindo sua porta estabelecida no login, para que outros usuários iniciem uma conexão. Ao receber uma nova conexão, gera um novo socket que é encapsulado em uma nova classe Módulo Servidor.
- **Módulo Servidor:** Classe responsável por encapsular o socket que recupera as mensagens dos outros usuários. Seu método ‘atende_comunicacao’ fica em uma Thread, criada pelo Coordenador de Servidores.
- **Interface:** Responsável por ler os comandos do stdin e responder de acordo, alterando a interface. Permite os comandos :q (logoff ou sair de uma conversa) e :r (refrescar as informações caso estejam desatualizadas). Também exibe para o usuário as informações seguindo o fluxo pensado para a aplicação.

Entrando na estrutura do código implementado e não mencionado acima, temos:

- **Estrutura.py**: guarda todas as informações globais referentes à aplicação do usuário.
- **Utils.py:** guarda as funções globais, como as de recuperação e construção da mensagem seguindo o padrão estabelecido para o trabalho.

Quanto às estruturas de dados para guardar as mensagens, usamos **dicionários** que tem como chaves os **pares de usuários**, mantendo registrado como valor uma **lista** com pares na forma (**usuario**, **mensagem**) para manter todo o histórico de mensagens. 

Para a notificação de “novas mensagens” nós usamos as mesmas chaves, mas como valor apenas um número identificando a quantidade de mensagens não lidas de uma conversa.

## Execução

1. Iniciar a aplicação do ServidorCentral.py com `python3 ServidorCentral.py`
2. Iniciar a aplicação do AplicacaoUsuario.py com `python3 AplicacaoUsuario.py`
3. Inserir os dados de usuario e porta para login
4. A aplicação foi iniciada