#!/bin/bash

mkdir -p benches/block/

for NUM in 8 16 32
do
  python benches/block.py --num ${NUM}
  cargo run -qr -- convert segmentation -i benches/block/block_${NUM}.npy -o benches/block/block_${NUM}.spn
done
