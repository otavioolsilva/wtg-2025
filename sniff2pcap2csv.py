# Script para gerar CSV a partir de pacotes farejados na rede salvos em um PCAP
#
# Esse código usa a biblioteca pyshark (um wrapper python para o tshark) para farejar pacotes na
# rede e salvá-los em um arquivo PCAP. Em seguida, os scripts do material suplementar do dataset
# CIC-IoT-2023 são usados para converter os dados para um arquivo CSV. Esses scripts usam a
# biblioteca dpkt para dissecar os pacotes.
#
# Não precisa ser executado com privilégios, mas o usuário deve estar no grupo 'wireshark'.
#
# Repositório pyshark: https://github.com/KimiNewt/pyshark
# Dataset CIC-IoT-2023: https://www.unb.ca/cic/datasets/iotdataset-2023.html
# Repositório dpkt: https://github.com/kbandla/dpkt

import argparse
import time
import psutil
from resource import *

import pyshark
from scripts_dataset_cic.Generating_dataset import main as pcap2csv

def parse_args():
    '''
        Parsing dos argumentos
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('interface', help='Interface a ser capturada pelo sniffer')
    parser.add_argument('-d', '--duration', action='store', default=30,
                        help='Duração da captura de pacotes em segundos')
    parser.add_argument('-o', '--output', action='store', default='output',
                        help='Nome dos arquivos de saída PCAP e CSV (sem extensão)')
    args = parser.parse_args()
    return args

def main(interface, duration, file_name):
    '''
        Fareja a interface de rede @interface por @duration segundos usando o Pyshark
        e gera um arquivo PCAP chamado @file_name.pcap. Depois disso, converte-o
        para um arquivo CSV chamado @file_name.pcap.csv.
    '''
    p = psutil.Process()
    p.cpu_percent(interval=None) # A documentação instrui a ignorar a primeira chamada desta
                                 # função, visto que o resultado dela é computado comparando
                                 # o uso atual de CPU com o da chamada anterior
    io_read_start = psutil.disk_io_counters(perdisk=True)['mmcblk0'][2] # Field read_bytes
    io_write_start = psutil.disk_io_counters(perdisk=True)['mmcblk0'][3] # Field write_bytes

    capture = pyshark.LiveCapture(interface=interface, output_file=file_name+'.pcap')
    print("Starting capture")
    start_time = time.time()
    capture.sniff(timeout=duration)
    print("Stopping capture")

    print("Starting the conversion PCAP -> CSV")
    pcap2csv([file_name+'.pcap'], 3) # Usando no máximo 3/4 threads da CPU

    end_time = time.time()
    io_read_end = psutil.disk_io_counters(perdisk=True)['mmcblk0'][2] # Campo read_bytes
    io_write_end = psutil.disk_io_counters(perdisk=True)['mmcblk0'][3] # Campo write_bytes

    print("\nUse of CPU: ", p.cpu_percent(interval=None), "%", sep='')
    print("Memory peak: ", getrusage(RUSAGE_SELF).ru_maxrss, "KB", sep='')
    print("Bytes read from disk:", (io_read_end - io_read_start)/(end_time - start_time), "bytes/s")
    print("Bytes wrote on disk:", (io_write_end - io_write_start)/(end_time - start_time), "bytes/s")

if __name__ == '__main__':
    args = parse_args()
    main(args.interface, int(args.duration), args.output)
