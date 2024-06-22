from rouge import Rouge 
from nltk.tokenize import word_tokenize
from nltk.translate.bleu_score import sentence_bleu
from nltk.translate.meteor_score import meteor_score
import nltk
nltk.download('wordnet')


reference = "Эталон"
hypothesis = "Генерация"

rouge = Rouge()
scores = rouge.get_scores(hypothesis, reference)

for score in scores:
    print("ROUGE-1")
    print("Precision:", round(score['rouge-1']['p']*100,3))
    print("Recall:", round(score['rouge-1']['r']*100,3))
    print("F-score:", round(score['rouge-1']['f']*100,3))
    print()
    print("ROUGE-2")
    print("Precision:", round(score['rouge-2']['p']*100,3))
    print("Recall:", round(score['rouge-2']['r']*100,3))
    print("F-score:", round(score['rouge-2']['f']*100,3))
    print()
    print("ROUGE-L")
    print("Precision:", round(score['rouge-l']['p']*100, 3))
    print("Recall:", round(score['rouge-l']['r']*100, 3))
    print("F-score:", round(score['rouge-l']['f']*100,3))
    print()



def calculate_bleu(reference, hypothesis):
    reference_tokens = word_tokenize(reference)
    hypothesis_tokens = word_tokenize(hypothesis)
    bleu_score = sentence_bleu([reference_tokens], hypothesis_tokens)
    print("BLEU score:", round(bleu_score*100,3))
    
calculate_bleu(reference, hypothesis)


