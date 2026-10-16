#!/usr/bin/env bash
# Sound clips: audio/originals/*.mp3 (as recorded) -> levelled clips for the app.
#   audio/<key>.mp3                         embedded in index.html (tools/embed_audio.py)
#   ios/SkiNav/Sounds/<key>.caf             notification sounds (phone locked)
#   android/app/src/main/res/raw/sfx_<key>.mp3   notification channel sounds
set -euo pipefail
cd "$(dirname "$0")/.."
declare -A SRC=( [passport]=efo_ze_val_tohrens [stoppp]=Stoppp [closed]=close_masage [speedking]=Avsha_ten_gazz
                 [today]=Lama_Hacol_metochnan [start]=Za_Bayzim_Beseder [stop]=ze_yavor_li [brief]=Yuval_hyiumi [steps]=Ani_Mastin )
NOTIFY="stoppp passport"
mkdir -p audio ios/SkiNav/Sounds android/app/src/main/res/raw
AF="silenceremove=start_periods=1:start_threshold=-55dB,acompressor=threshold=-20dB:ratio=3:attack=5:release=100:makeup=2,loudnorm=I=-15:TP=-1.5:LRA=11"
for k in "${!SRC[@]}"; do
  in="audio/originals/${SRC[$k]}.mp3"
  ffmpeg -v error -y -i "$in" -af "$AF" -ac 1 -ar 44100 -c:a libmp3lame -b:a 80k "audio/$k.mp3"
  if [[ " $NOTIFY " == *" $k "* ]]; then
    ffmpeg -v error -y -i "audio/$k.mp3" -ac 1 -ar 22050 -c:a pcm_s16le -f caf "ios/SkiNav/Sounds/$k.caf"
    cp "audio/$k.mp3" "android/app/src/main/res/raw/sfx_$k.mp3"
  fi
done
ls -la audio/*.mp3 ios/SkiNav/Sounds android/app/src/main/res/raw
