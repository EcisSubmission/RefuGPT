# RefuGPT
RefuGPT is a sophisticated chatbot, based on GPT-4, hosted on Telegram. RefuGPT aims to assist Ukrainian refugees in Switzerland. It utilizes the Langchain framework to connect GPT-4 to two distinct database. A official data containing official information (e.g. Swiss State, reputable NGOs, etc.) and community information (data scraped from open Telegram chats, where refugees exchange). This guide will walk you through the steps to download data  and then set up and start the Docker container for the chabot.

## Prerequisites
Before you begin, ensure you have the following installed:

Python 3.x
Docker and Docker Compose 3.X

1. **Clone the Repository**
   ```bash
   git clone https://github.com/EcisSubmission/RefuGPT
   cd RefuGPT
   ```
2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```   

## Data Retrieval with chroma_retrieve.py
The chroma_retrieve.py script is used to download necessary data for the RefugeeGPT bot. Follow these steps to use it:

1. **Download Official Data**
   ```bash
   python src/chroma_db/chroma_retrieve.py --method official
   ```   

The following code will download the official data and store them in a dedicated chroma database under the ```data/chroma/swiss_refugee_info_source/```. The code will scrape data defined in the file ```data/chroma/input/web_queries/websites_to_srape.txt```, if necessary more URLs can be added to enhance the knowledge base of the bot.

2. **Download Community Data**
   ```bash
    python src/chroma_db/scrapeTelegramChannelMessages.py -i data/chroma/input/telegram/switzerland_groups.txt -o data/chroma/input/df_telegram_for_chroma.csv
    python src/chroma_db/chroma_retrieve.py --method community
   ``` 
The following code will scrape data from 32 open Telegram groups within Switzerland. Please note that for scrapind data from Telegram an API key needs to be created [here](https://my.telegram.org) Afterwards, these messages are also fed into a chroma database under ```data/chroma/community_refugee_info/```.

## Build and Start the Docker Container:
After we have downloaded the data we can use Docker Compose to build and start the container, which will start the Telegrambot:
   ```bash
   docker-compose --docker/docker-compose.yaml up --build
   ```  
NOTE: To run the docker container an ```.env``` file is needed within the docker directory. The file  needs to container:
   ```bash
   telegram_refugees_ukr_ch_bot="YOUR_telegram_bot_key"
   telegram_bot_name="Your_telegram_bot_name"
   OPENAI_ORGANIZATION="YOUR_OPENAI_ORGANIZATION"
   OPENAI_API_KEY="YOUR_OPENAI_API_KEY"
   DEEPL_API_KEY="YOUR_DEEPL_API_KEY"
   ```  
These API keys can be obtained from [OpenAI](https://openai.com/blog/openai-api), [DeepL](https://www.deepl.com/pro-api?cta=header-pro-api) and the [Telegram Bot Father](https://telegram.me/BotFather). For the Telegram Bot Father, you will need to register your bot using the provided link.