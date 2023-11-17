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
from chat_testing import ChatBot

class ChatBotTester:

    def __init__(self, chatbot):
        self.bot = chatbot

    def run_tests(self, questions_path: str):
        questions = self.load_questions(questions_path)
        self.csv_path = "tests/loggs/" + questions_path.replace(".txt", ".csv").split("/")[-1]
        
        # If the CSV file doesn't exist, create it and write the headers
        with open(self.csv_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["question", "plain_response", "plain_infused_official_response", "plain_infused_official_response_top_K", "plain_infused_official_response_community_verified", "plain_infused_official_response_community_verified_top_K", "offical_response", "offical_response_top_K", "community_response", "community_response_top_K"])

        for question in tqdm(questions):
            plain_response, plain_infused_official_response, plain_infused_official_response_top_K, plain_infused_official_response_community_verified, plain_infused_official_response_community_verified_top_K, offical_response, offical_response_top_K, community_response, community_response_top_K = self.bot.chat(question, [])
            self.log_comparison(question, plain_response, plain_infused_official_response, plain_infused_official_response_top_K, plain_infused_official_response_community_verified, plain_infused_official_response_community_verified_top_K, offical_response, offical_response_top_K, community_response, community_response_top_K )

    def log_comparison(self, question, plain_response, plain_infused_official_response, plain_infused_official_response_top_K, plain_infused_official_response_community_verified, plain_infused_official_response_community_verified_top_K, offical_response, offical_response_top_K, community_response, community_response_top_K ):
        with open(self.csv_path, 'a', newline='') as csvfile:
            # Infused response typically returns in dict format, extracting the response content.
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([question, plain_response, plain_infused_official_response, plain_infused_official_response_top_K, plain_infused_official_response_community_verified, plain_infused_official_response_community_verified_top_K, offical_response, offical_response_top_K, community_response, community_response_top_K ])

    def load_questions(self, path: str) -> list:
        with open(path, 'r') as file:
            # Strip the whitespace and filter out empty lines
            questions = [line.strip() for line in file if line.strip()]
        return questions

if __name__ == "__main__":
    bot_instance = ChatBot()  # Initialize your ChatBot instance.
    tester = ChatBotTester(bot_instance)

    questions_path = 'tests/test_data/sample_questions_for_showing.txt'  # Update the path as necessary

    tester.run_tests(questions_path)
