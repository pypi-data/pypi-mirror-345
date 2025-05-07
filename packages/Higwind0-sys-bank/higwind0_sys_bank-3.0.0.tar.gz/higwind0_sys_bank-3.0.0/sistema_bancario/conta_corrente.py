from sistema_bancario.conta import conta


class ContaCorrente(conta):
    def __init__(self, numero, cliente, limite=500, limite_saque=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saque = limite_saque
        self._saques_realizados = 0

    def sacar(self, valor):
        _saques_realizados = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == "Saque"])

        excedeu_saques = self._saques_realizados >= self._limite_saque
        excedeu_limite = valor > self._limite

        if excedeu_saques:
            print("Limite de saques diários atingido.")
        if excedeu_limite:
            print("Valor do saque excede o limite de saque permitido.")
        else:
            return super().sacar(valor)
        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            Conta:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """
