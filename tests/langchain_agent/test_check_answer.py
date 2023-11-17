import unittest
import time
import csv
from tqdm import tqdm
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import sys
from threading import Lock
import os

sys.path.append("src/langchain_agent/")
from chat import ChatBot

lock = Lock()

def check_single_message(bot, message, csv_writer):
    with lock:  # Ensure that only one thread writes to the file at a time.
        response, rephrased_question, top_k_docs, chain_type = bot.chat(message, [])
        csv_writer.writerow([message, response, chain_type, top_k_docs])
    return None

def check_single_message_normal_GPT(bot, message):
    with lock:  # Ensure that only one thread writes to the file at a time.
        message_language = bot.detect_language(message)
        if message_language in bot.lang_dict.keys():
            message_language = bot.lang_dict[message_language]
        else:
            message_language = "english"
        
        if message_language != "english":
            message = bot.translate_to_english_deepL(message)

        response = bot.run_plain_normal_chain(message, message_language)
        return response

def retry_with_timeout(fn, *args, retries=3, timeout=5, **kwargs):
    for _ in range(retries):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(fn, *args, **kwargs)
            try:
                return future.result(timeout=timeout)
            except TimeoutError:
                logging.error(f"Function timed out, retrying... (Max retries={retries})")
                time.sleep(2)
    logging.error(f"Failed TRUE check for request due to TIMEOUT: {args[0]}")
    return None

class TestChatBot(unittest.TestCase):
    def setUp(self):
        self.bot = ChatBot()  # Assuming ChatBot is defined elsewhere in your code

    def test_check_answer(self):
        output_csv_path = 'tests/loggs/test_top70_kilian.csv'
        
        # Check if the directory exists, if not create it
        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
        
        # Check if the CSV file exists, if not create it and add headers
        if not os.path.exists(output_csv_path):
            with open(output_csv_path, 'w', newline='', encoding='utf-8-sig') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow(['Question', 'Answer', 'ChainType', 'TopKDocs'])

        already_answered_questions = set()
        
        # Read the already answered questions
        with open(output_csv_path, 'r', newline='', encoding='utf-8-sig') as file:
            csv_reader = csv.reader(file)
            next(csv_reader, None)  # Skip header row
            for row in csv_reader:
                already_answered_questions.add(row[0])

        non_answered_questions = []
        with open('tests/test_data/test_top70_kilian.txt', 'r', encoding='utf-8-sig') as file:
            questions = [line.strip() for line in file if not line.startswith('#')]
            non_answered_questions = [q for q in questions if q not in already_answered_questions]

        with open(output_csv_path, 'a', newline='', encoding='utf-8-sig') as file_out:
            csv_writer = csv.writer(file_out)
            
            for question in tqdm(non_answered_questions):
                check_single_message(self.bot, question, csv_writer) 
    
    def test_add_base_GPT_answers(self):
        input_csv_path = 'tests/loggs/test_top70_kilian.csv'
        temp_output_path = 'tests/loggs/temp_test_top70_kilian.csv'

        with open(input_csv_path, 'r', newline='', encoding='utf-8-sig') as infile, \
            open(temp_output_path, 'w', newline='', encoding='utf-8-sig') as outfile:
            
            csv_reader = csv.reader(infile)
            csv_writer = csv.writer(outfile)

            # Read and write header with the new column
            headers = next(csv_reader)
            headers.append('answer_base_gpt')
            csv_writer.writerow(headers)

            for row in tqdm(csv_reader, desc="Adding base GPT answers"):
                question = row[0]
                base_gpt_answer = check_single_message_normal_GPT(self.bot, question)
                row.append(base_gpt_answer)
                csv_writer.writerow(row)

        # Optionally: Replace the old CSV with the new one
        os.remove(input_csv_path)
        os.rename(temp_output_path, input_csv_path)


if __name__ == "__main__":
    unittest.main()
