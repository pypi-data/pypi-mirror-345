from sistema_bancario.pessoa_fisica import pessoaFisica
from sistema_bancario.conta_corrente import ContaCorrente
from sistema_bancario.deposito import Deposito
from sistema_bancario.saque import Saque


def main():
    sistema = sysBank()
    sistema.executar()


if __name__ == "__main__":
    main()


class sysBank:
    def __init__(self):
        self.clientes = []
        self.contas = []

    def menu(self):
        print("\nOlá, é muito bom te ver por aqui hoje!")
        print("Selecione uma das opções abaixo:")
        print("1 - Depósito")
        print("2 - Saque")
        print("3 - Extrato")
        print("4 - Cadastrar novo cliente")
        print("5 - Excluir Cliente")
        print("6 - Listar Clientes")
        print("7 - Cadastrar Conta Corrente")
        print("8 - Excluir Conta Corrente")
        print("9 - Listar Contas")
        print("10 - Sair")

        while True:
            try:
                opcao = int(input("Digite a opção desejada: "))
                if opcao in range(1, 11):
                    return opcao
                else:
                    print("Por favor, digite uma opção entre 1 e 10!")
            except ValueError:
                print("Por favor, digite um número válido!")

    def menu_retorno(self):
        while True:
            print("\nSelecione uma das opções abaixo:")
            print("1 - Voltar ao menu principal")
            print("2 - Sair do sistema")

            try:
                retorno = int(input("Digite a opção desejada: "))
                if retorno == 1:
                    self.executar()
                    break
                elif retorno == 2:
                    print("Obrigado por usar o sistema! Até logo!")
                    self.sair()
                    break
                else:
                    print("Por favor, digite uma opção entre 1 e 2!")
            except ValueError:
                print("Por favor, digite um número válido!")

    def executar(self):
        opcao = self.menu()

        if opcao == 1:
            self.realizar_deposito()
        if opcao == 2:
            self.realizar_saque()
        if opcao == 3:
            self.exibir_extrato()
        if opcao == 4:
            self.cadastrar_cliente()
        if opcao == 5:
            self.excluir_cliente()
        if opcao == 6:
            self.listar_clientes()
        if opcao == 7:
            self.cadastrar_conta()
        if opcao == 8:
            self.excluir_conta_corrente()
        if opcao == 9:
            self.listar_contas()
        if opcao == 10:
            self.sair()

    def selecionar_cliente(self):
        cpf = input("Digite o CPF do cliente: ")
        for cliente in self.clientes:
            if cliente.cpf == cpf:
                return cliente
        print("Cliente não encontrado.")
        return None

    def realizar_deposito(self):
        cliente = self.selecionar_cliente()
        if cliente and cliente.contas:
            valor = float(input("Digite o valor do depósito: "))
            deposito = Deposito(valor)
            cliente.realizar_transacao(deposito)
            print(
                f"Depósito de R$ {valor:.2f} realizado com sucesso na conta de {cliente.nome}.")
        self.menu_retorno()

    def realizar_saque(self):
        cliente = self.selecionar_cliente()
        if cliente and cliente.contas:
            valor = float(input("Informe o valor para saque: "))
            saque = Saque(valor)
            cliente.realizar_transacao(saque)
        self.menu_retorno()

    def mostrar_extrato(self):
        cliente = self.selecionar_cliente()
        if cliente and cliente.contas:
            conta = cliente.contas[0]
            print("\n--- HISTÓRICO ---")
            for transacao in conta.historico.transacoes:
                print(
                    f"{transacao['data']} - {transacao['tipo']}: R$ {transacao['valor']:.2f}")
        self.menu_retorno()

    def cadastrar_cliente(self):
        cpf = input("CPF: ")
        nome = input("Nome: ")
        data_nascimento = input("Data de nascimento (DD-MM-AAAA): ")
        endereco = input("Endereço: ")
        novo_cliente = pessoaFisica(cpf, nome, data_nascimento, endereco)
        self.clientes.append(novo_cliente)
        print("Cliente cadastrado com sucesso!")
        self.menu_retorno()

    def excluir_cliente(self):
        cpf = input("Digite o CPF do cliente a ser removido: ")
        self.clientes = [c for c in self.clientes if c.cpf != cpf]
        print("Cliente removido, se existia.")
        self.menu_retorno()

    def listar_clientes(self):
        if not self.clientes:
            print("Nenhum cliente cadastrado.")
        for cliente in self.clientes:
            print(
                f"{cliente.nome} | CPF: {cliente.cpf} | Endereço: {cliente.endereco}")
        self.menu_retorno()

    def cadastrar_conta(self):
        cliente = self.selecionar_cliente()
        if cliente:
            numero = len(self.contas) + 1
            conta = ContaCorrente(numero, cliente)
            cliente.adicionar_conta(conta)
            self.contas.append(conta)
            print("Conta criada com sucesso!")
        self.menu_retorno()

    def excluir_conta(self):
        numero = int(input("Informe o número da conta a excluir: "))
        self.contas = [c for c in self.contas if c.numero != numero]
        print("Conta excluída, se existia.")
        self.menu_retorno()

    def listar_contas(self):
        if not self.contas:
            print("Nenhuma conta cadastrada.")
        for conta in self.contas:
            print(
                f"Agência: {conta.agencia} | Conta: {conta.numero} | Cliente: {conta.cliente.nome}")
        self.menu_retorno()

    def sair(self):
        print("Obrigado por utilizar nosso sistema. Até logo!")


if __name__ == "__main__":
    sistema = sysBank()
    sistema.executar()
