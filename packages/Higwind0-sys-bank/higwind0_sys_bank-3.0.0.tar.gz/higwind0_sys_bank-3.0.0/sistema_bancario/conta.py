from sistema_bancario.historico import Historico


class conta:
    def __init__(self, numero, cliente):
        self._saldo = 0.0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print(f"Depósito de R$ {valor:.2f} realizado com sucesso.")
        else:
            raise ValueError("Valor inválido para depósito.")

        return True

    def sacar(self, valor):
        saldo = self._saldo

        if valor > saldo:
            raise ValueError("Saldo insuficiente.")
        if valor <= 0:
            raise ValueError("Valor de saque deve ser maior que zero.")
        elif valor < saldo:
            self._saldo -= valor
            print(f"Saque de R$ {valor:.2f} realizado com sucesso.")
            return True
        else:
            raise ValueError("Valor inválido para saque.")

        return False
