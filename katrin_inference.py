from katrin_hm import HM

import collections
import os

from param import args

import numpy as np

from tqdm import tqdm
import torch
import torch.nn as nn
from torch.utils.data.dataloader import DataLoader

if args.tsv:
    from fts_tsv.hm_data_tsv import HMTorchDataset, HMEvaluator, HMDataset
else:
    from fts_lmdb.hm_data import HMTorchDataset, HMEvaluator, HMDataset

from src.vilio.transformers.optimization import AdamW, get_linear_schedule_with_warmup
from utils.pandas_scripts import clean_data

from entryU import ModelU

#import transformers
#import tokenizers
#import pytorch_pretrained_bert as ppb
#assert 'bert-large-cased' in ppb.modeling.PRETRAINED_MODEL_ARCHIVE_MAP
# Aufruf mit : python hm.py --seed 129 --model U \
# --test dev_seen --lr 1e-5 --batchSize 8 --tr bert-large-cased --epochs 5 --tsv \
# --num_features 36 --num_pos 6 --loadfin $loadfin --exp U36

# python katrin_inference.py --seed 129 --model U \
# --test test_seen,test_unseen --lr 1e-5 --batchSize 8 --tr bert-large-cased --epochs 5 --tsv \
# --num_features 36 --num_pos 6 --loadfin ./kaggle/input/viliou36/LASTtraindev.pth --exp U36

# ./kaggle/input/viliou36/LASTtrain.pth

DataTuple = collections.namedtuple("DataTuple", 'dataset loader evaluator')


def get_tuple(splits: str, bs: int, shuffle=False, drop_last=False) -> DataTuple:

    dset = HMDataset(splits)

    tset = HMTorchDataset(splits)
    print("tset")
    print(tset)
    evaluator = HMEvaluator(tset)
    data_loader = DataLoader(
        tset, batch_size=bs,
        shuffle=shuffle, num_workers=args.num_workers,
        drop_last=drop_last, pin_memory=True
    )

    return DataTuple(dataset=dset, loader=data_loader, evaluator=evaluator)


def main():
    # Build Class
    hm = HM()

    print("test")

    for split in args.test.split(","):
        # Anthing that has no labels:
        if 'test' in split: # katrin_test_seen

            print(hm.predict(
                get_tuple(split, bs=args.batch_size,
                          shuffle=False, drop_last=False),
                dump=os.path.join(
                    args.output, '{}_{}.csv'.format(args.exp, split))
            ))


print("test")
main()
