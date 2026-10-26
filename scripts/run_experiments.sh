#!/usr/bin/env bash
# 3 cenários x 3 quantidades de instâncias x 3 cargas = 27 execuções. CSVs em results/
set -euo pipefail
cd "$(dirname "$0")/.."

INSTANCES=${INSTANCES:-"1 2 3"}
USERS_LIST=${USERS_LIST:-"10 100 1000"}
SCENARIOS=${SCENARIOS:-"1 2 3"}
DURATION=${DURATION:-60s}
SPAWN_RATE=${SPAWN_RATE:-50}
mkdir -p results; chmod 777 results
declare -A SLUG=( [1]=cenario-1-imagem-1mb [2]=cenario-2-texto-400kb [3]=cenario-3-imagem-300kb )

docker compose up -d mysql
for n in $INSTANCES; do
  echo "=== $n instância(s) do WordPress ==="
  export NGINX_CONF="./nginx/nginx-$n.conf"
  docker compose stop nginx wordpress1 wordpress2 wordpress3 >/dev/null
  svcs=""; for i in $(seq 1 "$n"); do svcs="$svcs wordpress$i"; done
  docker compose up -d --no-deps $svcs
  sleep 10
  docker compose up -d --no-deps --force-recreate nginx
  until [[ "$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:8080/?name=${SLUG[1]}")" == "200" ]]; do sleep 3; done

  # confere o balanceamento: deve haver exatamente $n upstreams distintos
  seen=$(for _ in $(seq 1 12); do curl -sI "http://localhost:8080/?name=${SLUG[1]}" | grep -i '^x-upstream' || true; done | sort -u | wc -l)
  echo "upstreams distintos observados: $seen (esperado: $n)"

  for s in $SCENARIOS; do
    for _ in 1 2 3; do curl -s -o /dev/null "http://localhost:8080/?name=${SLUG[$s]}"; done   # aquecimento
    for u in $USERS_LIST; do
      run="s${s}_i${n}_u${u}"
      echo "--> $run"
      docker compose --profile test run --rm --no-deps -T \
        -e SCENARIO="$s" -e LOCUST_USERS="$u" -e LOCUST_SPAWN_RATE="$SPAWN_RATE" \
        -e LOCUST_RUN_TIME="$DURATION" -e LOCUST_CSV="/results/$run" locust
      sleep 10
    done
  done
done
echo "Pronto. Rode: python3 scripts/analyze.py"
