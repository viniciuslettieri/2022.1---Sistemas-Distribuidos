# Laboratório 5 - Sistemas Distribuídos

Neste Laboratório, implemento um prototocolo de replicação de cópia primária com escrita local. Ou seja, a partir de diversas réplicas, estaticamente definidas no arquivo elemento com a lista `replicas`, queremos manter a consistência entre as instâncias obrigando com que aquelas que escrevem precisem captar a posse de outra. Além disso, as alterações devem ser propagadas para as demais.

Os elementos possuem as capacidades de:
1. ler o valor atual de X na replica.
2. ler o historico de alterações do valor de X.
3. alterar o valor de X.
4. propagar as mudanças locais.

Ou seja, é possível acumular alterações em uma instância e propagar a última delas quando necessário. Além disso, quando a posse deixar de uma instância para outra, aquela é obrigada a propagar suas alterações.

Para utilizar o sistema distribuído, é necessário executar o `elemento.py` para cada uma das N portas da lista `replicas` e escolher uma das portas para cada um.