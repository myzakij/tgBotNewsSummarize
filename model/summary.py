from transformers import MBartTokenizer, MBartForConditionalGeneration

model_path = "pukislav/sum_14_ru_88"
tokenizer = MBartTokenizer.from_pretrained(model_path)
model = MBartForConditionalGeneration.from_pretrained(model_path)

def summarize_text(text, max_length=1024, max_summary_length=300, num_beams=3, early_stopping=True, no_repeat_ngram_size=5):

    input_ids = tokenizer([text], max_length=max_length, padding="max_length", truncation=True, return_tensors="pt")["input_ids"]

    decode_input_ids = model.generate(input_ids=input_ids, num_beams=num_beams, max_length=max_summary_length, early_stopping=early_stopping, no_repeat_ngram_size=no_repeat_ngram_size)[0]
 
    summary = tokenizer.decode(decode_input_ids, skip_special_ids=True)
    
    return summary


# text =  """
#         """
# print(summarize_text(text))