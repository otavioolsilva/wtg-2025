# Script para gerar arquivo CSV diretamente de pacotes farejados na rede
#
# Esse código usa a biblioteca pypcap para farejar pacotes na rede e os scripts do
# material suplementar do dataset CIC-IoT-2023 para salvar estes dados em um arquivo CSV.
# Esses scripts usam a biblioteca dpkt para dissecar os pacotes.
#
# Privilégios são necessários pelo pypcap para farejar a rede.
#
# Repositório pypcap: https://github.com/pynetwork/pypcap
# Dataset CIC-IoT-2023: https://www.unb.ca/cic/datasets/iotdataset-2023.html
# Repositório dpkt: https://github.com/kbandla/dpkt

import argparse
import psutil
from resource import *
import time
import threading

import pcap
from scripts_dataset_cic.Feature_extraction_WOPCAP import Feature_extraction

def parse_args():
    '''
        Parsing dos argumentos
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('interface', help='Interface a ser capturada pelo sniffer')
    parser.add_argument('-d', '--duration', action='store', default=30,
                        help='Duração da captura de pacotes em segundos')
    parser.add_argument('-o', '--output', action='store', default='output',
                        help='Nome do arquivo CSV de saída (sem extensão)')
    parser.add_argument('-w', '--window', action='store', default=10,
                        help='Tamanho da janela de pacotes CSV para serem enviados para processamento')
    parser.add_argument('-b', '--buffer', action='store', default=5000,
                        help='Tamanho do buffer de pacotes a serem processados')
    args = parser.parse_args()
    return args

class thread_args():
    '''
        Classe que contém os argumentos a serem compartilhados entre as threads
        Permite trabalhar com mais de uma thread no futuro
    '''
    def __init__(self, buf_size):
        self.buf_size = buf_size
        self.buf = [[]] * self.buf_size # Buffer circular que guarda grupos de pacotes a serem processados
        self.front = 0
        self.rear = 0
        self.sem_empty = threading.Semaphore(self.buf_size)
        self.sem_full = threading.Semaphore(0)
        self.stop = threading.Event()
        self.file_name = ''

def main(interface, duration, file_name, window_size, buffer_size):
    '''
        Fareja a interface de rede @interface por @duration segundos usando a biblioteca pypcap
        e gera um arquivo CSV chamado @file_name.csv diretamente dos dados capturados
    '''
    p = psutil.Process()
    p.cpu_percent(interval=None) # A documentação instrui a ignorar a primeira chamada desta
                                 # função, visto que o resultado dela é computado comparando
                                 # o uso atual de CPU com o da chamada anterior
    io_read_start = psutil.disk_io_counters(perdisk=True)['mmcblk0'][2] # Field read_bytes
    io_write_start = psutil.disk_io_counters(perdisk=True)['mmcblk0'][3] # Field write_bytes

    sniffer = pcap.pcap(name=interface, immediate=True)

    fe = Feature_extraction()
    pkt_buffer = []

    ta = thread_args(buffer_size)
    ta.file_name = file_name
    thread = threading.Thread(target=fe.pcap_evaluation_caller, args=[ta]) # Enquanto esse código faz o sniffing,
    thread.start()                                                         # a outra thread processa os pacotes

    print('Starting capture')
    start_time = time.time()

    for ts, buf in sniffer:
        if time.time() - start_time > duration:
            break

        pkt_buffer.append((ts, buf))

        if len(pkt_buffer) >= window_size:
            ta.sem_empty.acquire()
            ta.buf[ta.rear] = pkt_buffer.copy()
            ta.rear = (ta.rear + 1) % ta.buf_size
            ta.sem_full.release()

            pkt_buffer = []

    if len(pkt_buffer) > 0:
        ta.sem_empty.acquire()
        ta.buf[ta.rear] = pkt_buffer.copy()
        ta.rear = (ta.rear + 1) % ta.buf_size
        ta.sem_full.release()

    print("Stopping capture")
    sniffer.close()

    ta.stop.set()
    thread.join()

    end_time = time.time()
    io_read_end = psutil.disk_io_counters(perdisk=True)['mmcblk0'][2] # Campo read_bytes
    io_write_end = psutil.disk_io_counters(perdisk=True)['mmcblk0'][3] # Campo write_bytes

    print("\nUse of CPU: ", p.cpu_percent(interval=None), "%", sep='')
    print("Memory peak: ", getrusage(RUSAGE_SELF).ru_maxrss, "KB", sep='')
    print("Bytes read from disk:", (io_read_end - io_read_start)/(end_time - start_time), "bytes/s")
    print("Bytes wrote on disk:", (io_write_end - io_write_start)/(end_time - start_time), "bytes/s")

if __name__ == '__main__':
    args = parse_args()
    main(args.interface, int(args.duration), args.output, int(args.window), int(args.buffer))
