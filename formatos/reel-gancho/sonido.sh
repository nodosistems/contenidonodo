#!/usr/bin/env bash
# Audio propio (sin copyright) del reel «recepcionista»: base rítmica suave + whoosh en cada cambio
# de escena + pings en las notificaciones + tics del reloj + campanita en el CTA.
# Para otro reel: ajusta D (duración en s) y los tiempos (ms) de W, P, T y CHIME a las escenas del guion.
# Uso: bash sonido.sh salida.m4a   (otro reel: D=… W="…" P="…" T="…" EXTRA=… CHIME=… bash sonido.sh salida.m4a; T="" = sin tics)
set -e; OUT=$(realpath -m "${1:-audio.m4a}"); TMP=$(mktemp -d); cd "$TMP"
D=${D:-21.6}; W=${W-"2300 4600 8400 10800 13600 16300 18600"}; P=${P-"4850 5330 5810 6290 6770 7250"}; T=${T-"8400 8900 9400 9900 10400"}; EXTRA=${EXTRA:-11500}; CHIME=${CHIME:-18850}
ffmpeg -loglevel error -y -f lavfi -i "aevalsrc='0.55*sin(2*PI*52*mod(t,0.6))*exp(-mod(t,0.6)*12)*lt(t,18.6)+0.05*(sin(2*PI*220*t)+sin(2*PI*277.18*t)+sin(2*PI*329.63*t))*(0.6+0.4*sin(2*PI*0.25*t))':s=44100:d=$D" -af "afade=t=in:d=0.3,afade=t=out:st=$(echo "$D-1.2"|bc):d=1.2" base.wav
ffmpeg -loglevel error -y -f lavfi -i "anoisesrc=d=0.35:c=pink:a=0.5" -af "highpass=f=900,lowpass=f=6000,afade=t=in:d=0.18,afade=t=out:st=0.18:d=0.17" whoosh.wav
ffmpeg -loglevel error -y -f lavfi -i "aevalsrc='0.35*(sin(2*PI*1318*t)+0.5*sin(2*PI*1975*t))*exp(-t*14)':s=44100:d=0.35" ping.wav
ffmpeg -loglevel error -y -f lavfi -i "aevalsrc='0.4*sin(2*PI*2400*t)*exp(-t*90)':s=44100:d=0.06" tick.wav
ffmpeg -loglevel error -y -f lavfi -i "aevalsrc='0.3*(sin(2*PI*880*t)+sin(2*PI*1318.5*t)+0.6*sin(2*PI*1760*t))*exp(-t*3)':s=44100:d=1.6" chime.wav
inputs="-i base.wav"; filt=""; n=1
add(){ inputs="$inputs -i $1"; filt="$filt[$n]adelay=$2|$2[a$n];"; n=$((n+1)); }
for ms in $W; do add whoosh.wav $ms; done; for ms in $P; do add ping.wav $ms; done; for ms in $T; do add tick.wav $ms; done
add whoosh.wav $EXTRA; add chime.wav $CHIME
mix="[0]"; for i in $(seq 1 $((n-1))); do mix="$mix[a$i]"; done
ffmpeg -loglevel error -y $inputs -filter_complex "${filt}${mix}amix=inputs=$n:normalize=0:duration=first,alimiter=limit=0.9,aformat=channel_layouts=stereo" -c:a aac -b:a 160k "$OUT"
rm -rf "$TMP"; echo "ok $OUT"
