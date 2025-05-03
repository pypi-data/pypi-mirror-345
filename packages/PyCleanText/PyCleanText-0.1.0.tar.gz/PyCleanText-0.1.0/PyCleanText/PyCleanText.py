import string
import re

def PyCleanText(file_path, output_file_path='cleaned_output.txt'):
    stopwords = set([
        "a", "about", "above", "after", "again", "against", "ain", "all", "am",
        "an", "and", "any", "are", "aren", "aren't", "as", "at", "be", "because",
        "been", "before", "being", "below", "between", "both", "but", "by", "can",
        "couldn", "couldn't", "d", "did", "didn", "didn't", "do", "does", "doesn",
        "doesn't", "doing", "don", "don't", "down", "during", "each", "few", "for",
        "from", "further", "had", "hadn", "hadn't", "has", "hasn", "hasn't", "have",
        "haven", "haven't", "having", "he", "her", "here", "hers", "herself", "him",
        "himself", "his", "how", "i", "if", "in", "into", "is", "isn", "isn't", "it",
        "it's", "its", "itself", "just", "ll", "m", "ma", "me", "mightn", "mightn't",
        "more", "most", "mustn", "mustn't", "my", "myself", "needn", "needn't", "no",
        "nor", "not", "now", "o", "of", "off", "on", "once", "only", "or", "other",
        "our", "ours", "ourselves", "out", "over", "own", "re", "s", "same", "shan",
        "shan't", "she", "she's", "should", "should've", "shouldn", "shouldn't",
        "so", "some", "such", "t", "than", "that", "that'll", "the", "their",
        "theirs", "them", "themselves", "then", "there", "these", "they", "this",
        "those", "through", "to", "too", "under", "until", "up", "very", "was",
        "wasn", "wasn't", "we", "were", "weren", "weren't", "what", "when", "where",
        "which", "while", "who", "whom", "why", "will", "with", "won", "won't",
        "wouldn", "wouldn't", "y", "you", "you'd", "you'll", "you're", "you've",
        "your", "yours", "yourself", "yourselves"
    ])

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()

        text = text.lower()
        text = re.sub(r'http\S+|www\.\S+', '', text)
        text = re.sub(r'[\.\-]{2,}', ' ', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = ''.join(char for char in text if ord(char) < 128)
        text = text.translate(str.maketrans('', '', string.punctuation))
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'[@#]\w+', '', text)
        text = re.sub(r'[^\w\s]', '', text)
        text = ' '.join(text.split())
        
        words = text.split()
        words = [word for word in words if word not in stopwords]

        deduped_words = []
        prev_word = None
        for word in words:
            if word != prev_word:
                deduped_words.append(word)
            prev_word = word

        cleaned_text = ' '.join(deduped_words)

        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_text)
        
        return print(f"Successfully saved cleaned text to {output_file_path}")
    
    except FileNotFoundError:
        return print(f"Error: The file at {file_path} was not found.")
    except Exception as e:
        return print(f"An error occurred: {str(e)}")