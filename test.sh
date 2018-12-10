#!/bin/bash
declare -a locales

# Load file into array.
readarray locales < wikilocale.txt

# Explicitly report array content.
# let i=0
# while (( ${#locales[@]} > i )); do
    # # printf "Locale $i : ${locales[i++]}\n"
# done

declare -a dates

# Load file into array.
readarray dates < dates.txt

# # Explicitly report array content.
# let i=0
# while (( ${#dates[@]} > i )); do
    # # printf "Date $i : ${dates[i++]}\n"
# done

# declare -a mirrors

# # Load file into array.
# readarray mirrors < mirrors.txt

# # Explicitly report array content.
# let i=0
# while (( ${#mirrors[@]} > i )); do
    # printf "Mirror $i : ${mirrors[i++]}\n"
# done

declare -a projects

# Load file into array.
readarray projects < projects.txt

# # Explicitly report array content.
# let i=0
# while (( ${#projects[@]} > i )); do
    # printf "Projects $i : ${projects[i++]}\n"
# done

for ((m = 1; m < 3; m++))
do
for ((j = 0; j < ${#dates[@]}; j++))
do
for ((k = 0; k < ${#projects[@]}; k++))
do
for ((l = 0; l < ${#locales[@]}; l++))
do
python wdcln.py -m $m -d ${dates[j]} -p ${projects[k]} -l ${locales[l]} -r 5
done
done
done
done
