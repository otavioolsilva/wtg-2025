Conjunto de scripts utilizados para performar experimentos gerando arquivos CSV a partir de tráfego de rede. Utilizam-se scripts do material suplementar do dataset [CIC-IoT-2023](https://www.unb.ca/cic/datasets/iotdataset-2023.html)[^1] para processar os pacotes e gerar o CSV final[^2]. Os cenários considerados para experimentação são:

[^1]: Neto, E. C. P., Dadkhah, S., Ferreira, R., Zohourian, A., Lu, R., and Ghorbani, A. A. (2023). CICIoT2023: A Real-Time Dataset and Benchmark for Large-Scale Attacks in IoT Environment. Sensors, 23(13).

[^2]: Os scripts foram adaptados para o contexto de uso desse trabalho, em geral apenas adequações para que fossem invocados externamente e retornassem métricas de desempenho. As diferenças entre a versão original e a atual podem ser observadas pelo histórico de commits do repositório.

- Farejamento da rede, armazenamento do tráfego em arquivo PCAP e conversão para CSV[^3];
- Farejamento da rede e conversão direta do tráfego para CSV, provendo os pacotes de 10 em 10 para a thread responsável pelas entradas do arquivo final;
- Farejameto da rede e conversão direta do tráfego para CSV, provendo todos os pacotes em único conjunto para a thread responsável pelas entradas do arquivo final.

[^3]: Nesse caso, os scripts do dataset CIC-IoT-2023 são utilizados inclusive para carregar os arquivos PCAP. O processamento é paralelizado usando múltiplos processos, cada qual sendo responsável por reportar suas próprias métricas de desempenho. Assim, para uma avaliação completa, é necessário tomar os valores obtidos proporcionalmente ao tempo de execução total do código na consideração final.

As métricas consideradas para análise são: uso de CPU, pico de uso de memória, leitura e escrita em disco, número de pacotes processados (número de linhas do CSV final) e tempo total de execução.

Base de códigos utilizada no artigo "Adequação Online de Rastros de Tráfego de Rede nos Clientes para Alimentar Sistemas de Detecção de Intrusão", submetido para o VIII Workshop de Trabalhos de Iniciação Científica e de Graduação ([WTG 2025](https://sbrc.sbc.org.br/2025/pt_br/viii-workshop-de-trabalhos-de-iniciacao-cientifica-e-de-graduacao-wtg-2025/)), parte do 43º Simpósio Brasileiro de Redes de Computadores e Sistemas Distribuídos ([SBRC 2025](https://sbrc.sbc.org.br/2025/pt_br/)), disponível nos [Anais Estendidos do simpósio na SBC Open Library](https://sol.sbc.org.br/index.php/sbrc_estendido/article/view/35888).

### Dependências

Todos os experimentos foram conduzidos usando Python 3.11.2 no lado do cliente. As dependências usadas e suas versões foram:

- Script `sniff2csv.py`: [Pypcap](https://pypi.org/project/pypcap/) (v1.3.0).
- Script `sniff2pcap2csv.py`: [Pyshark](https://pypi.org/project/pyshark/) (v0.6).
- Scripts do CIC-IoT-2023: [tqdm](https://pypi.org/project/tqdm/) (v4.66.6), [numpy](https://pypi.org/project/numpy/) (v1.26.4), [pandas](https://pypi.org/project/pandas/) (v2.2.3), [dpkt](https://pypi.org/project/dpkt/) (v1.9.8) e [Scapy](https://pypi.org/project/scapy/) (v2.6.0).
- Para avaliação de performance em todos os scripts: [psutil](https://pypi.org/project/psutil/) (v6.1.0).

Para gerar a simulação de tráfego de rede, a aplicação usada foi a [iperf3](https://iperf.fr/) (v3.17.1).

### Como executar

Para rodar todos os cenários, utilize o Bash script `run-tests.sh` passando como argumentos o caminho do interpretador Python e o endereço IP do servidor iperf3. Por padrão, serão executados 5 vezes cada um dos cenários com taxas de bits de 5Mbits/s, 10Mbits/s, 15Mbits/s, 20Mbits/s e 25Mbits/s.

Os scripts Python estão configurados para farejar a interface de rede "eth0" por 30 segundos por padrão, esses parâmetros podem ser alterados no código ou na invocação dos scripts. Note que os códigos que fazem uso das bibliotecas Pypcap e Scapy precisam ser executados com privilégios, enquanto o que utiliza o Pyshark apenas requer que o usuário esteja no grupo "wireshark".
