# Copyright 2024 Advanced Micro Devices
#
# Licensed under the Apache License v2.0 with LLVM Exceptions.
# See https://llvm.org/LICENSE.txt for license information.
# SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception

import sys, argparse
import torch
import torch.nn as nn
import torch_mlir
from transformers import BartForCausalLM, AutoTokenizer

# import from e2eshark/tools to allow running in current dir, for run through
# run.pl, commutils is symbolically linked to allow any rundir to work
sys.path.insert(0, "../../../tools/stubs")
from commonutils import E2ESHARK_CHECK_DEF

# Create an instance of it for this test
E2ESHARK_CHECK = dict(E2ESHARK_CHECK_DEF)

# model origin: https://huggingface.co/facebook/bart-large
test_modelname = "facebook/bart-large"
tokenizer = AutoTokenizer.from_pretrained(test_modelname)
model = BartForCausalLM.from_pretrained(
    test_modelname,
    num_labels=2,
    output_attentions=False,
    output_hidden_states=False,
    attn_implementation="eager",
    torchscript=True,
)
model.to("cpu")
model.eval()
prompt = "What is nature of our existence?"
encoding = tokenizer(prompt, return_tensors="pt")
E2ESHARK_CHECK["input"] = encoding["input_ids"].cpu()
E2ESHARK_CHECK["output"] = model(E2ESHARK_CHECK["input"])
model_response = model.generate(
    E2ESHARK_CHECK["input"],
    do_sample=True,
    top_k=50,
    max_length=100,
    top_p=0.95,
    temperature=1.0,
)
print("Prompt:", prompt)
print("Response:", tokenizer.decode(model_response[0]))
print("Input:", E2ESHARK_CHECK["input"])
print("Output:", E2ESHARK_CHECK["output"])
# For geneartive AI models, input is int and should be kept that way for
# casted models as well
E2ESHARK_CHECK["inputtodtype"] = False
