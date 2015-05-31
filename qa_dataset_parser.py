import re

from theano_util import *

import pdb

def only_words(line):
    ps = re.sub(r'[^a-zA-Z0-9]', r' ', line)
    ws = re.sub(r'(\W)', r' \1 ', ps) # Put spaces around punctuations
    ns = re.sub(r'(\d+)', r' <number> ', ws) # Put spaces around numbers
    hs = re.sub(r'-', r' ', ns) # Replace hyphens with space
    rs = re.sub(r' +', r' ', hs) # Reduce multiple spaces into 1
    return rs

def clean_sentence(line):
    ps = re.sub(r'[^a-zA-Z0-9_\.\?\!]', ' ', line) # Split on punctuations and hex characters
    ws = re.sub(r'(\W)', r' \1 ', ps) # Put spaces around punctuations
    ns = re.sub(r'(\d+)', r' <number> ', ws) # Put spaces around numbers
    hs = re.sub(r'-', r' ', ns) # Replace hyphens with space
    rs = re.sub(r' +', r' ', hs) # Reduce multiple spaces into 1
    return rs

def get_sentences(line):
    ps = re.sub(r'[^a-zA-Z0-9_\.\?\!]', ' ', line) # Split on punctuations and hex characters
    s = re.sub(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s', '\t', ps) # Split on sentences
    ws = re.sub(r'(\W)', r' \1 ', s) # Put spaces around punctuations
    ns = re.sub(r'(\d+)', r' <number> ', ws) # Put spaces around numbers
    hs = re.sub(r'-', r' ', ns) # Replace hyphens with space
    rs = re.sub(r' +', r' ', hs) # Reduce multiple spaces into 1

    return rs.split('\t')

def parse_qa_dataset(input_dir, word_id=0, word_to_id={}, update_word_ids=True):
    dataset = []
    questions = []

    article_files = set()
    with open(input_dir + '/question_answer_pairs.txt') as f:
        for line in f:
            # Skip first line
            if 'ArticleFile' in line:
                continue

            line = line.strip()

            # Skip empty lines
            if len(line) == 0:
                continue

            parts = line.split('\t')
            if len(parts) != 6:
                print("Malformed line: " + line)
                continue

            question = parts[1]
            answer = parts[2]
            answer = only_words(answer).strip().lower()

            article_name = parts[5]

            # There are other fields in the dataset, use them later if you want

            # This dataset has repeated questions. What to do?

            # Don't answer questions with more than 1 word answers
            if len(answer) == 0 or len(answer.split(' ')) > 1:
                # Skip for now
                continue

            question_parts = question.split('\t')
            tokens = clean_sentence(question_parts[0]).strip().split()
            tokens = filter(lambda x: len(x.strip()) > 0, tokens)
            tokens = map(lambda x: x.lower(), tokens)
            question_tokens = tokens
            if update_word_ids:
                for token in (tokens + [answer]):
                    if token not in word_to_id:
                        word_to_id[token] = word_id
                        word_id += 1

            article_no = len(questions)

            article_file = input_dir + '/' + article_name + '.txt.clean'
            article_files.add(article_file)
            questions.append([article_no, article_file, [question_tokens], answer])

    article_data = {}
    for article_file in article_files:
        # Get all statements in the dataset for this question

        s_file = open(article_file)
        statements = []
        for statement in s_file:
            if len(statement.strip()) == 0:
                continue

            sentences = get_sentences(statement.strip())

            for sentence in sentences:
                tokens = sentence.strip().split()
                tokens = filter(lambda x: len(x.strip()) > 0, tokens)
                tokens = map(lambda x: x.lower(), tokens)

                article = tokens
                statements.append(article)
                if update_word_ids:
                    for token in tokens:
                        if token not in word_to_id:
                            word_to_id[token] = word_id
                            word_id += 1

        article_data[article_file] = statements

    for question in questions:
        question[2] = article_data[question[1]] + question[2]
        question[1] = -1

    questions_seq = map(lambda x: transform_ques_weak(x, word_to_id, word_id), questions)
    return dataset, questions_seq, word_to_id, word_id

if __name__ == "__main__":
    train_file = sys.argv[1]

    train_dataset, train_questions, word_to_id, num_words = parse_qa_dataset(train_file)
    #test_dataset, test_questions, _, _ = parse_dataset_weak(test_file, word_id=num_words, word_to_id=word_to_id, update_word_ids=False)

    # each element of train_questions contains: [article_no, line_no, [lists of indices of statements and question], index of answer word]
    import pprint
    pprint.pprint(word_to_id)
    print num_words
