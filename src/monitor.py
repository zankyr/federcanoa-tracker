import json
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from loguru import logger



class WebsiteMonitor:
    def __init__(self, config_path):
        """
        Initialize the monitor using a config file
        :param config_path: Path to the configuration file
        """
        self.base_dir = Path(__file__).parent.absolute()

        self.config = self.load_config(config_path)

        self.setup_logging()

        # Initialize other attributes
        self.site_url = self.config['site_url']
        self.courses_url = self.site_url + self.config['courses_url']
        self.keyword = self.config['keyword'].lower()
        self.known_courses = self.load_known_courses()
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    @staticmethod
    def load_config(config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Error loading configuration: {e}")

    def setup_logging(self):
        """Configure loguru logger"""
        log_file = self.base_dir / 'monitor.log'

        # Remove any existing handlers
        logger.remove()

        # Add handlers for both file and console
        logger.add(log_file,
                   rotation="1 day",
                   retention="30 days",
                   format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
                   level="INFO",
                   compression="zip")

        logger.add(lambda msg: print(msg),
                   format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
                   level="INFO")

    def load_known_courses(self):
        """Load previously found courses from storage"""
        known_docs_path = self.base_dir / 'known_courses.json'
        try:
            with open(known_docs_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []

    def save_known_courses(self):
        """Save current courses to storage"""
        known_docs_path = self.base_dir / 'known_courses.json'
        with open(known_docs_path, 'w', encoding='utf-8') as f:
            json.dump(self.known_courses, f, ensure_ascii=False, indent=2)

    def send_telegram_notification(self, new_documents):
        """Send notification via Telegram"""
        if not all([self.config.get('telegram_bot_token'), self.config.get('telegram_chat_id')]):
            raise ValueError("Telegram configuration missing")

        telegram_api_url = f"https://api.telegram.org/bot{self.config['telegram_bot_token']}/sendMessage"

        message = "🔔 Nuovi documenti trovati:\n\n"
        for doc in new_documents:
            message += f"📄 {doc['title']}\n"
            message += f"🔗 {doc['link']}\n\n"

        try:
            response = requests.post(telegram_api_url, data={
                'chat_id': self.config['telegram_chat_id'],
                'text': message,
                'parse_mode': 'HTML'
            })
            response.raise_for_status()
            logger.success("Telegram notification sent successfully")
        except Exception as e:
            raise ValueError(f"Failed to send Telegram notification: {e}")

    def check_website(self):
        """Check website for new documents"""
        try:
            logger.info(f"Checking website: {self.courses_url}")
            response = self.session.get(self.courses_url, headers=self.headers, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            component_section = soup.find('section', id='component')
            if not component_section:
                logger.warning("Could not find component section")
                return

            scheda_div = component_section.find('div', class_='scheda')
            if not scheda_div:
                logger.warning("Could not find scheda div")
                return

            documents = []

            for p_tag in scheda_div.find_all('p'):
                link_tag = p_tag.find('a')
                if link_tag:
                    title = link_tag.text.strip()
                    link = link_tag['href']
                    if link.startswith('/'):
                        link = f"{self.site_url.rstrip('/')}{link}"

                    if self.keyword.lower() in title.lower():
                        documents.append({
                            'title': title,
                            'link': link,
                            'date_found': datetime.now().isoformat()
                        })

            new_documents = []
            for doc in documents:
                if not any(known_doc['link'] == doc['link'] for known_doc in self.known_courses):
                    new_documents.append(doc)
                    self.known_courses.append(doc)

            # https://www.federcanoa.it/images/comitatiregionali/lombardia/INDIZIONE_CORSO_SECONDO_LIVELLO_PIATTA_2023.pdf
            # https://www.federcanoa.it/images/comitatiregionali/lombardia/INDIZIONE_CORSO_SECONDO_LIVELLO_PIATTA_2023.pdf
            # https://www.federcanoa.it/lombardia.html?id=25&layout=menu4/images/comitatiregionali/lombardia/INDIZIONE_CORSO_SECONDO_LIVELLO_PIATTA_2023.pdf

            if new_documents:
                logger.success(f"Found {len(new_documents)} new documents")
                for doc in new_documents:
                    logger.info(f"New document: {doc['title']}")
                    logger.info(f"Link: {doc['link']}")
                self.save_known_courses()
                self.send_telegram_notification(new_documents)
            else:
                logger.info("No new documents found")

        except requests.RequestException as e:
            logger.error(f"Request error: {e}")
        except Exception as e:
            logger.exception(f"Error checking website: {str(e)}")
