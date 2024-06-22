import torch
from torch import nn

from transformers import MBartForConditionalGeneration, MBartConfig, MBartTokenizer


def remove_ignore_keys_(state_dict):
    ignore_keys = [
        "encoder.version",
        "decoder.version",
        "model.encoder.version",
        "model.decoder.version",
        "_float_tensor",
    ]
    for k in ignore_keys:
        state_dict.pop(k, None)


def _make_linear_from_tensor(t):
    vocab_size, emb_size = t.shape
    lin_layer = nn.Linear(vocab_size, emb_size, bias=False)
    lin_layer.weight.data = t.data
    return lin_layer


def convert_fairseq_mbart_checkpoint(checkpoint_path, hf_config_path="facebook/mbart-large-en-ro"):
    chkpt = torch.load(checkpoint_path, map_location="cpu")
    state_dict = chkpt["model"]
    remove_ignore_keys_(state_dict)
    vocab_size = state_dict["encoder.embed_tokens.weight"].shape[0]
    state_dict["shared.weight"] = state_dict["decoder.embed_tokens.weight"]
    output_projection = state_dict.pop("decoder.output_projection.weight")

    mbart_config = MBartConfig.from_pretrained(hf_config_path, vocab_size=vocab_size)
    model = MBartForConditionalGeneration(mbart_config).eval()
    model.model.load_state_dict(state_dict)
    model.lm_head = _make_linear_from_tensor(output_projection)
    model.final_logits_bias = torch.zeros((1, vocab_size))
    return model

model = convert_fairseq_mbart_checkpoint("/conv/model.pt")
torch.save(model.state_dict(), "/conv/conv_model.bin")
tokenizer = MBartTokenizer.from_pretrained("facebook/mbart-large-cc25")
tokenizer.save_pretrained("C:/Users/YOUR_PATH/conv")