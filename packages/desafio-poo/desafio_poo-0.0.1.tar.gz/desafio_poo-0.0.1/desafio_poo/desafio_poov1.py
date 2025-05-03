import textwrap
from abc import ABC, abstractmethod

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.conta = None

    def realizar_transacao(self, transacao):
        if self.conta:
            self.conta.adicionar_transacao(transacao)
        else:
            print("Cliente não possui conta associada.")

    def adicionar_conta(self, conta):
        self.conta = conta

class PessoaFisica(Cliente):
    def __init__(self, nome, cpf, data_nascimento, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
        cliente.adicionar_conta(self)

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    def sacar(self, valor):
        if valor <= 0:
            print("O valor do saque deve ser positivo.")
            return False
        if valor > self._saldo:
            print("Saldo insuficiente.")
            return False

        self._saldo -= valor
        print(f"Saque de R${valor:.2f} realizado com sucesso.")
        return True

    def depositar(self, valor):
        if valor <= 0:
            print("O valor do depósito deve ser positivo.")
            return False

        self._saldo += valor
        print(f"Depósito de R${valor:.2f} realizado com sucesso.")
        return True

    def adicionar_transacao(self, transacao):
        if transacao.registrar(self):
            self._historico.adicionar(transacao)

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = float(limite)
        self._limite_saques = int(limite_saques)
        self._numero_saques = 0

    def sacar(self, valor):
        if self._numero_saques >= self._limite_saques:
            print("Limite de saques diários excedido.")
            return False
        if valor > self._limite:
            print("Valor excede o limite de saque.")
            return False

        if super().sacar(valor):
            self._numero_saques += 1
            return True
        return False

class Historico:
    def __init__(self):
        self._transacoes = []

    def adicionar(self, transacao):
        self._transacoes.append(transacao)

    @property
    def transacoes(self):
        return self._transacoes

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        return conta.sacar(self.valor)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        return conta.depositar(self.valor)

def menu():
    menu_texto = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu_texto))

def localizar_cliente(cpf, clientes):
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None

def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = localizar_cliente(cpf, clientes)

    if cliente:
        print("Já existe um cliente com esse CPF.")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, número - bairro - cidade/UF): ")

    novo_cliente = PessoaFisica(nome, cpf, data_nascimento, endereco)
    clientes.append(novo_cliente)
    print("Cliente criado com sucesso!")

def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = localizar_cliente(cpf, clientes)

    if not cliente:
        print("Cliente não encontrado.")
        return

    conta = ContaCorrente.nova_conta(cliente, numero_conta)
    contas.append(conta)
    print("Conta criada com sucesso!")

def realizar_deposito(clientes):
    cpf = input("Informe o CPF: ")
    cliente = localizar_cliente(cpf, clientes)

    if not cliente or not cliente.conta:
        print("Cliente ou conta não encontrado.")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)
    cliente.realizar_transacao(transacao)

def realizar_saque(clientes):
    cpf = input("Informe o CPF: ")
    cliente = localizar_cliente(cpf, clientes)

    if not cliente or not cliente.conta:
        print("Cliente ou conta não encontrado.")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)
    cliente.realizar_transacao(transacao)

def exibir_extrato(clientes):
    cpf = input("Informe o CPF: ")
    cliente = localizar_cliente(cpf, clientes)

    if not cliente or not cliente.conta:
        print("Cliente ou conta não encontrado.")
        return

    print("\n================ EXTRATO ================")
    transacoes = cliente.conta._historico.transacoes

    if not transacoes:
        print("Não foram realizadas movimentações.")
    else:
        for transacao in transacoes:
            tipo = transacao.__class__.__name__
            print(f"{tipo}: R${transacao.valor:.2f}")

    print(f"\nSaldo: R${cliente.conta.saldo:.2f}")
    print("==========================================")

def listar_contas(contas):
    for conta in contas:
        print("=" * 30)
        print(f"Agência: {conta._agencia}")
        print(f"C/C: {conta._numero}")
        print(f"Titular: {conta._cliente.nome}")

def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            realizar_deposito(clientes)
        elif opcao == "s":
            realizar_saque(clientes)
        elif opcao == "e":
            exibir_extrato(clientes)
        elif opcao == "nu":
            criar_cliente(clientes)
        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)
        elif opcao == "lc":
            listar_contas(contas)
        elif opcao == "q":
            break
        else:
            print("Operação inválida. Tente novamente.")

if __name__ == "__main__":
    main()
