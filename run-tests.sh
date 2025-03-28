#!/bin/bash

if [ $# -ne 2 ]; then
  echo "Usage: '$0 [Python interpreter path] [server IP]'"
  exit 1
fi

run() {
  for i in {1..5}; do # Cinco iterações
    printf "'$1' - Bitrate $3: Test case $i ==============================\n"

    time $1 & # Rodando o script Python em segundo plano
    pid=$!

    sleep 20 # Aguardando 20s antes de iniciar o fluxo de dados na rede,
             # o script Python pode tomar algum tempo para iniciar

    # iperf UDP
    iperf3 -c $2 --time 10 --verbose --udp --bitrate $3

    sleep 15
    ping $2 -c 1 > /dev/null # Apenas para quebrar o loop do pypcap, visto que
                             # ele não possui mecanismo próprio para isso

    wait $pid 2> /dev/null # Garante que o processo Python terminou

    printf "Number of lines in the output file: "
    wc -l *.csv # Conta o número de linhas no CSV final
    sudo rm -f *.csv *.pcap # Apaga os arquivos de saída

    printf "\n\n"
  done
}

for bitrate in 5M 10M 15M 20M 25M; do
  printf "====================== BITRATE $bitrate ======================\n\n"

  printf "Running tests on sniff2csv.py with limited window\n\n"
  command="sudo $1 sniff2csv.py eth0 --duration 30 --window 10 --buffer 5000"
  run "$command" $2 $bitrate

  printf "Running tests on sniff2csv.py with unlimited window\n\n"
  command="sudo $1 sniff2csv.py eth0 --duration 30 --window 50000 --buffer 10"
  run "$command" $2 $bitrate

  printf "Running tests on sniff2pcap2csv.py\n\n"
  command="$1 sniff2pcap2csv.py eth0 --duration 30"
  run "$command" $2 $bitrate

  printf "\n\n\n"
done
