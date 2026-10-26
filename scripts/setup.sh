#!/usr/bin/env bash
# Prepara o ambiente: gera arquivos de teste, sobe a stack (1 instância), instala o WordPress e cria os 3 posts.
set -euo pipefail
cd "$(dirname "$0")/.."
export NGINX_CONF=./nginx/nginx-1.conf

python3 scripts/gen_assets.py
docker compose up -d mysql
# Sobe só o wordpress1 primeiro (evita 3 instâncias copiando arquivos ao mesmo tempo)
docker compose up -d --no-deps wordpress1
docker compose up -d --no-deps --force-recreate nginx

echo "Aguardando WordPress..."
until [[ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/)" =~ ^(200|301|302)$ ]]; do sleep 3; done

docker compose --profile tools run --rm wpcli wp --url=http://localhost:8080 core is-installed 2>/dev/null || \
docker compose --profile tools run --rm wpcli wp --url=http://localhost:8080 core install \
  --title="Sistemas Distribuidos" --admin_user=admin --admin_password=admin123 \
  --admin_email=admin@example.com --skip-email
docker compose --profile tools run --rm --entrypoint sh wpcli /scripts/create_posts.sh

for s in cenario-1-imagem-1mb cenario-2-texto-400kb cenario-3-imagem-300kb; do
  echo "$s -> $(curl -s -o /dev/null -w '%{http_code} %{size_download} bytes' "http://localhost:8080/?name=$s")"
done
echo "Setup concluído. Se instalou pelo navegador no Trabalho 2, o 'core install' é ignorado automaticamente."
