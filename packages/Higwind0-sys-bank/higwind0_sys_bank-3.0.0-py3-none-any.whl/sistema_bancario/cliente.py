from sistema_bancario.conta import conta


class cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, transacao):
        if not self.contas:
            print("Cliente não possui contas.")
            return False

        conta = self.contas[0]
        return transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)
