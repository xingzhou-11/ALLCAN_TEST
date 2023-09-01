for i in $@
do
    echo $i
    python3 download.py $i "zephyr.signed.bin" "socketcan" "can0" 1000000
done
