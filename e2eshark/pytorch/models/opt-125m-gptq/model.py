import sys, argparse
import torch
import torch.nn as nn
import torch_mlir
from transformers import AutoModelForCausalLM, AutoTokenizer, GPTQConfig

# import from e2eshark/tools to allow running in current dir, for run through
# run.pl, commutils is symbolically linked to allow any rundir to work
sys.path.insert(0, "../../../tools/stubs")
from commonutils import E2ESHARK_CHECK_DEF

# Create an instance of it for this test
E2ESHARK_CHECK = dict(E2ESHARK_CHECK_DEF)

# model origin: https://huggingface.co/jlsilva/facebook-opt-125m-gptq4bit
test_modelname = "facebook/opt-125m"
quantizedmodelname = "jlsilva/facebook-opt-125m-gptq4bit"
kwargs = {
    "torch_dtype": torch.float32,
    "trust_remote_code": True,
}
quantization_config = GPTQConfig(bits=8, disable_exllama=True)
kwargs["quantization_config"] = quantization_config
kwargs["device_map"] = "cpu"
model = AutoModelForCausalLM.from_pretrained(quantizedmodelname, **kwargs)
# model.output_hidden_states = False
tokenizer = AutoTokenizer.from_pretrained(test_modelname)
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
