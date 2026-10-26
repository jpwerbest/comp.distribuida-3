#!/bin/sh
# Executado dentro do contêiner wpcli. --url define HTTP_HOST (o wp-config usa o host da requisição).
set -e
cd /var/www/html
wpc() { wp --url=http://localhost:8080 "$@"; }

# remove posts de execuções anteriores (idempotente)
for slug in cenario-1-imagem-1mb cenario-2-texto-400kb cenario-3-imagem-300kb; do
  ids=$(wpc post list --post_type=post --name="$slug" --format=ids)
  [ -n "$ids" ] && wpc post delete $ids --force >/dev/null
done

wpc post create /assets/text_400kb.html --post_title="Cenario 2 - texto 400kb" \
   --post_name=cenario-2-texto-400kb --post_status=publish --porcelain

for spec in "1:img_1mb.jpg:cenario-1-imagem-1mb" "3:img_300kb.jpg:cenario-3-imagem-300kb"; do
  n=${spec%%:*}; rest=${spec#*:}; img=${rest%%:*}; slug=${rest#*:}
  pid=$(wpc post create --post_title="Cenario $n - imagem" --post_name="$slug" \
        --post_status=publish --post_content="x" --porcelain)
  att=$(wpc media import "/assets/$img" --post_id="$pid" --porcelain)
  f=$(wpc post meta get "$att" _wp_attached_file)
  wpc post update "$pid" --post_content="<p>Post do cenario $n</p><img src=\"/wp-content/uploads/$f\" alt=\"imagem\">"
done
wpc post list --fields=ID,post_name,post_status
