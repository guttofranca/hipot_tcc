import serial
import time
import binascii
from decimal import Decimal, getcontext


class hipot:
    getcontext().prec = 2
    ##########################################CONSTANTES USADAS NOS COMANDOS############################################
    # comando para iniciar os testes
    START_TEST = bytes.fromhex("AB 01 70 01 22 6C")

    # comando para parar o teste ao falhar
    STOP_TEST = bytes.fromhex("AB 01 70 01 21 6D")

    # comando para recuperar os resultados dos testes
    RESULT = bytes.fromhex("AB 01 70 03 B1 00 D7 04")

    # dicionário com os codígos retornados pelo hipot com os resultados de um teste
    RESULT_CODE = {"11": "HIGH FAIL", "12": "LOW FAIL", "13": "ARC FAIL", "14": "I/O FAIL",
                   "15": "NO OUTPUT", "16": "VOLTAGE OVER", "17": "CURRENT OVER", "70": "STOP",
                   "71": "USER INTERRUPT", "72": "CAN NOT TEST", "73": "TESTING", "74": "PASS",
                   "75": "SKIPPED", "79": "GFI TRIPPED", "7A": "SLAVE FAIL", "7B": "SHORT FAIL"}

    # delay necessário usado entre o comando para iniciar
    # os teste e ir buscar a resposta no equipamento
    DELAY = 0.5

    #####################################FIM DAS CONSTANTES USADAS NOS COMANDOS#########################################

    # ---------------------------------------------------------------------------------------------------------------------

    ##########################################VARIÁVEIS GLOBAIS USADAS#####################################################
    def __init__(self):
        # lista com o retorno do resultado_1
        self.return_list_result_1 = []

        # tempo que o primeiro teste for iniciado
        self.start_time_1 = 0

        # gurdará o valor da corrente medida pelo hipot(byes hexadecimal)
        self.result_value_1 = 0
        self.result_value_2 = 0
        self.result_value_3 = 0
        self.result_value_4 = 0

        # variável usada para guardar o resultado do teste
        self.result_status = "PASS"

        # variável usada para guardar o codigo do resultado do teste
        self.result_code = "74"

        # variável usada para guardar valor da corrente retornada pelo hipot
        self.current = 0

        # variável usada para guardar o valor da tensão retornadada pelo hipot
        self.voltage = 0

        # string que irá guardar o valor da string com o resultado final do teste
        # que será usada para exibiçao ao usuário final
        self.result_string = ""

    ###################################FIM DAS VARIÁVEIS GLOBAIS USADAS####################################################

    # ---------------------------------------------------------------------------------------------------------------------

    ############################FUNÇÕES USADAS PARA ENVIAR COMANDOS AO HIPOT###############################################

    # FUNÇÃO PARA ENVIAR COMANDO DE INICIAR TESTES
    # OU PARA ENVIAR COMANDO PARA PARAR OS TESTES
    def start_stop_tests(self, command):

        try:

            with serial.Serial(port='COM2', baudrate=9600, parity=serial.PARITY_NONE) as porta:

                if command == self.START_TEST:
                    porta.write(command)
                if command == self.STOP_TEST:
                    porta.write(command)
                    porta.write(command)

                # marcando momento em que teste é iniciado
                self.start_time_1 = time.time()

        except Exception as error:
            print(f"Erro: {error}")

    # FUNÇÃO PARA ENVIAR COMANDO PARA RECUPERAR RESULTADOS DO TESTE
    def get_result(self):

        while time.time() - self.start_time_1 < self.DELAY:
            pass

        self.return_list_result_1 = []

        with serial.Serial(port='COM2', baudrate=9600, parity=serial.PARITY_NONE) as porta:

            while True:

                self.return_list_result_1 = []
                porta.write(self.RESULT)

                # importante: LOOP obrigatoriamente de 23
                for _ in range(23):
                    rcv = porta.read()
                    rcv_str = binascii.hexlify(rcv).decode("utf-8")
                    self.return_list_result_1.append(rcv_str)

                if self.return_list_result_1[7] != "73":
                    break

    # método que irá retornar o valor de corrente medido pelo hipot
    # a partir dos bytes devolvidos pelo equipamento
    def get_current_value(self, byte1, byte2, byte3, byte4):

        byte_all = str(byte1 + byte2 + byte3 + byte4).strip()
        value_int = int(byte_all, 16)

        # multiplicando por 100n (unidade) e por 1000(converter para mA)
        self.current = Decimal(value_int) * Decimal(100e-9) * Decimal(1000)
        return self.current

    # função irá trabalhar sobre a lista que armazena o retorno do hipot
    # para devolver os status de teste, como se o teste aprovou ou reprovou
    # o código de erro e o valor da medida.
    def return_results(self):

        # guardará os bytes relativos ao valor da corrente medida pelo hipot
        self.result_value_1 = self.return_list_result_1[12]
        self.result_value_2 = self.return_list_result_1[13]
        self.result_value_3 = self.return_list_result_1[14]
        self.result_value_4 = self.return_list_result_1[15]

        self.current = self.get_current_value(self.result_value_4, self.result_value_3, self.result_value_2,
                                              self.result_value_1)

        if self.return_list_result_1[7] == "74":

            self.result_status = "PASS"
            self.result_string = ""
            self.result_string = self.result_string + f"Result: {self.result_status}\n"
            self.result_string = self.result_string + f"Current: {self.current}mA"
        else:
            self.result_status = "FAIL"
            self.result_string = ""
            self.result_string = self.result_string + f"Result: {self.result_status}\n"
            # se o teste apresentar falha, deve ser parado
            # para que não fique apitando e para que o
            # operador não precise apertar o botão stop
            # no equipamento.
            self.start_stop_tests(self.STOP_TEST)

            self.result_string = self.result_string + f"Error code: {self.return_list_result_1[7]}\n"
            self.result_string = self.result_string + (
                f"Description: {self.RESULT_CODE[self.return_list_result_1[7]]}\n")
            self.result_string = self.result_string + f"Current: {self.current}mA"

        return self.result_string

############################FIM DAS FUNÇÕES USADAS PARA ENVIAR COMANDOS AO HIPOT#######################################

# testando funções
# if __name__ == "__main__":
# envia comando para executar um teste
# start_stop_tests(START_TEST)

# coleta de resultados do teste
# get_result()

# resultado, codigo, corrente = return_results()
# print(f"Result: {resultado}")

# if result_status == "FAIL":
# print(f"Error code: {return_list_result_1[7]}")
# print(f"Description: {results_code[return_list_result_1[7]]}")

# print(f"Current: {corrente}mA")
