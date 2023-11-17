import unittest
import time
from tqdm import tqdm
import logging
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from src.langchain_agent.chat import ChatBot

logging.basicConfig(filename='tests/loggs/test_chat.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def retry_with_timeout(fn, *args, retries=3, timeout=5, **kwargs):
    for _ in range(retries):
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(fn, *args, **kwargs)
            try:
                return future.result(timeout=timeout)
            except TimeoutError:
                # logger.error(f"Function timed out, retrying... (Max retries={retries})")
                time.sleep(2)  # Delay before retrying
    logger.error(f"Failed TRUE check for request due to TIMEOUT: {args[0]}")
    return None

class TestChatBot(unittest.TestCase):
    def setUp(self):
        self.bot = ChatBot()

    def test_check_message_content(self):
        def check_true_request(request):
            out = self.bot.check_message_content(request)
            out_bool = out == "1"
            if not out_bool:
                logger.error(f"Failed TRUE check for request: {request}, got {out}")

        def check_false_request(request):
            out = self.bot.check_message_content(request)
            out_bool = out == "0"
            if not out_bool:
                logger.error(f"Failed FALSE check for request: {request}, got {out}")

        with open("tests/test_data/requests_true.txt", "r") as file:
            true_requests = [line.strip() for line in file if not line.startswith("#")]

        with open("tests/test_data/requests_false.txt", "r") as file:
            false_requests = [line.strip() for line in file if not line.startswith("#")]

        with ThreadPoolExecutor() as executor:
            list(tqdm(executor.map(lambda x: retry_with_timeout(check_true_request, x), true_requests), total=len(true_requests), desc="Testing true requests"))

        with ThreadPoolExecutor(  ) as executor:
            list(tqdm(executor.map(lambda x: retry_with_timeout(check_false_request, x), false_requests), total=len(false_requests), desc="Testing false requests"))


    def test_detect_language(self):
        test_cases = {
            "Hello, I need a Status S": "en",
            "Hallo, ich brauche einen Status S": "de",
            "Bonjour, j'ai besoin d'un Status S": "fr",
            "Salve, ho bisogno di uno Status S": "it",
            "Доброго дня, мені потрібен статус S": "uk",
            "Здравствуйте, мне нужен статус S": "ru"
        }

        for message, expected_lang in test_cases.items():
            detected_language = self.bot.detect_language(message)
            if detected_language != expected_lang:
                logger.error(f"Expected language '{expected_lang}' for message '{message}', but detected '{detected_language}'")

    def test_translate_to_english(self):
        test_cases = {
            "Hello, I need a Status S": "Hello, I need a Status S",  # English to English
            "Hallo, ich brauche einen Status S": "Hello, I need a Status S",  # German to English
            "Salut, j'ai besoin d'un statut S": "Hello, I need a Status S",  # French to English
            "Ciao, ho bisogno di uno stato S": "Hello, I need a Status S",  # Italian to English
            "Привіт, мені потрібен статус S": "Hello, I need a Status S",  # Ukrainian to English
            "Привет, мне нужен статус S": "Hello, I need a Status S"  # Russian to English
        }

        for message, expected_translation in test_cases.items():
            translated_message = self.bot.translate_to_english(message)
            if translated_message != expected_translation:
                logger.error(f"Expected translation '{expected_translation}' for message '{message}', but got '{translated_message}'")


if __name__ == "__main__":
    unittest.main()
