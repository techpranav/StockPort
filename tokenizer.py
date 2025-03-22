import nltk

nltk.download("punkt")
from nltk.tokenize import word_tokenize
from transformers import pipeline


def count_tokens(text):
    """
    Count tokens in the text using a simple word tokenizer.
    (For more advanced tokenization, consider libraries like tiktoken.)
    """
    tokens = word_tokenize(text)
    return len(tokens)


def reduce_prompt(prompt, max_tokens=100, min_tokens=30):
    """
    If the prompt exceeds max_tokens, use a summarization model to reduce its length.
    Otherwise, return the prompt unchanged.
    """
    current_tokens = count_tokens(prompt)
    print(f"Original token count: {current_tokens}")

    if current_tokens <= max_tokens:
        return prompt
    else:
        # Use a summarization model to reduce the text.
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        # The model expects a single string of text.
        summary = summarizer(prompt, max_length=max_tokens, min_length=min_tokens, do_sample=False)
        reduced_text = summary[0]['summary_text']
        print(f"Reduced token count: {count_tokens(reduced_text)}")
        return reduced_text


if __name__ == "__main__":
    input_prompt = input("Enter your prompt:\n")
    new_prompt = reduce_prompt(input_prompt, max_tokens=35000, min_tokens=30)
    print("\nReduced Prompt:")
    print(new_prompt)
