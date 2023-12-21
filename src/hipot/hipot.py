import serial
import time
import binascii
from decimal import Decimal, getcontext


getcontext().prec = 2
##########################################CONSTANTES USADAS NOS COMANDOS###############################################
# comando para iniciar os testes
START_TEST = bytes.fromhex("AB 01 70 01 22 6C")

# comando para parar o teste ao falhar
STOP_TEST = bytes.fromhex("AB 01 70 01 21 6D")

# comando para recuperar os resultados dos testes
RESULT = bytes.fromhex("AB 01 70 03 B1 00 D7 04")

#####################################FIM DAS CONSTANTES USADAS NOS COMANDOS############################################

# ---------------------------------------------------------------------------------------------------------------------

##########################################VARIÁVEIS GLOBAIS USADAS#####################################################
# lista com o retorno do resultado_1
return_list_result_1 = []

# tempo que o primeiro teste for iniciado
start_time_1 = 0

# guardará se foi aprovado ou reprovado no teste1
result_status = ""

# guradará o valor da corrente medida pelo hipot
result_value_1 = 0
result_value_2 = 0
result_value_3 = 0
result_value_4 = 0

# delay necessário usado entre o comando para iniciar
# os teste e ir buscar a resposta no equipamento
delay = 0.5

# dicionário com os codígos retornados pelo hipot com os resultados de um teste
results_code = {"11": "HIGH FAIL", "12": "LOW FAIL", "13": "ARC FAIL", "14": "I/O FAIL",
                "15": "NO OUTPUT", "16": "VOLTAGE OVER", "17": "CURRENT OVER", "70": "STOP",
                "71": "USER INTERRUPT", "72": "CAN NOT TEST", "73": "TESTING", "74": "PASS",
                "75": "SKIPPED", "79": "GFI TRIPPED", "7A": "SLAVE FAIL", "7B": "SHORT FAIL"}

# variável usada para guardar o resultado do teste
result = "PASS"

# variável usada para guardar o codigo do resultado do teste
result_code = "74"


###################################FIM DAS VARIÁVEIS GLOBAIS USADAS####################################################

# ---------------------------------------------------------------------------------------------------------------------

############################FUNÇÕES USADAS PARA ENVIAR COMANDOS AO HIPOT###############################################


# FUNÇÃO PARA ENVIAR COMANDO DE INICIAR TESTES
# OU PARA ENVIAR COMANDO PARA PARAR OS TESTES
def start_stop_tests(command):

    try:

        with serial.Serial(port='COM2', baudrate=9600, parity=serial.PARITY_NONE) as porta:

            if command == START_TEST:
                porta.write(command)
            if command == STOP_TEST:
                porta.write(command)
                porta.write(command)

            # marcando momento em que teste é iniciado
            global start_time_1
            start_time_1 = time.time()

    except Exception as error:
        print(f"Erro: {error}")


# FUNÇÃO PARA ENVIAR COMANDO PARA RECUPERAR RESULTADOS DO TESTE
def get_result():
    global start_time_1
    global return_list_result_1
    global result_status

    global delay

    while time.time() - start_time_1 < delay:
        pass

    return_list_result_1 = []

    with serial.Serial(port='COM2', baudrate=9600, parity=serial.PARITY_NONE) as porta:

        while True:

            return_list_result_1 = []
            porta.write(RESULT)

            # importante: LOOP obrigatoriamente de 23
            for _ in range(23):
                rcv = porta.read()
                rcv_str = binascii.hexlify(rcv).decode("utf-8")
                return_list_result_1.append(rcv_str)

            if return_list_result_1[7] != "73":
                break


def get_current_value(byte1,byte2,byte3,byte4):

    byte_all = str(byte1+byte2+byte3+byte4).strip()
    value_int = int(byte_all,16)

    # multiplicando por 100n (unidade) e por 1000(converter para mA)
    current = Decimal(value_int)*Decimal(100e-9)*Decimal(1000)
    return current

# função irá trabalhar sobre a lista que armazena o retorno do hipot
# para devolver os status de teste, como se o teste aprovou ou reprovou
# o código de erro e o valor da medida.
def return_results():
    global return_list_result_1
    global result_status
    global result_code
    global result_value_1
    global result_value_2
    global result_value_3
    global result_value_4

    if return_list_result_1[7] == "74":
        result_status = "PASS"
    else:
        result_status = "FAIL"
        # se o teste apresentar falha, deve ser parado
        # para que não fique apitando e para que o
        # operador não precise apertar o botão stop
        # no equipamento.
        start_stop_tests(STOP_TEST)

    result_value_1 = return_list_result_1[12]
    result_value_2 = return_list_result_1[13]
    result_value_3 = return_list_result_1[14]
    result_value_4 = return_list_result_1[15]

    current = get_current_value(result_value_4,result_value_3,result_value_2,result_value_1)

    return result_status, result_code, current


############################FIM DAS FUNÇÕES USADAS PARA ENVIAR COMANDOS AO HIPOT#######################################

# testando funções
if __name__ == "__main__":
    # envia comando para executar um teste
    start_stop_tests(START_TEST)

    # coleta de resultados do teste
    get_result()

    resultado, codigo, corrente = return_results()
    print(f"Result: {resultado}")

    if result_status == "FAIL":
        print(f"Error code: {return_list_result_1[7]}")
        print(f"Description: {results_code[return_list_result_1[7]]}")

    print(f"Current: {corrente}mA")
