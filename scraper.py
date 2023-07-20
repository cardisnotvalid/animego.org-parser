import re
import json
import httpx
import asyncio
import logging
from bs4 import BeautifulSoup

import config
from random import choice, uniform
from rich.console import Console
from rich.progress import Progress


class Scraper:
    def __init__(self, console: Console) -> None:
        self.console = console
        self.anime_data_list = []
        self.anime_preview_list = []
        self.client = httpx.AsyncClient(verify=False)
    
    def get_anime_data_list(self) -> list:
        return self.anime_data_list
    
    def get_anime_preview_list(self) -> list:
        return sorted(self.anime_preview_list, key=lambda item: item["id"])

    async def run(self) -> None:
        await self.fetch_all_anime_previews()
        await self.fetch_all_anime_data()

    async def fetch_anime_data(self, url: str, id: int, progress: Progress, task_id: int) -> None:
        while True:
            headers = {"user-agent": self.get_user_agent()}
            try:
                response = await self.client.get(url, headers=headers)
                logging.debug(f"Processing url: {url} | Status code: {response.status_code}")
                
                if response.status_code == 200:
                    break
                elif response.status_code == 404:
                    progress.advance(task_id, 1)
                    return
                else:
                    await asyncio.sleep(uniform(5, 10))
            except Exception as ex:
                await asyncio.sleep(uniform(5, 10))
                
        soup = BeautifulSoup(response.text, "lxml")
        
        description = soup.select_one(".description")
        thumbnail = soup.select_one("div:nth-child(2) > img")
        screenshots = [f"https://animego.org{screen['href']}" for screen in soup.select(".screenshots-block > a")]
        trailer = soup.select_one(".video-item")
        
        rows = soup.select_one("dl.row")
        dt_items = [dt.get_text(" ", strip=True) for dt in rows.select("dt") if dt.text]
        dd_items = [dd.get_text(" ", strip=True) for dd in rows.select("dd") if dd.text]
        
        anime_data = {}
        anime_data["id"] = id
        anime_data["title"] = soup.select_one(".anime-title > div > h1").get_text(strip=True)
        anime_data["synonyms"] = [synonym.get_text(strip=True) for synonym in soup.select("div.anime-synonyms > ul > li")]
        anime_data.update({self._translate(key): value for key, value in zip(dt_items[:-1], dd_items[:-1])})
        anime_data["characters"] = [character.get_text(" ", strip=True) for character in rows.select("dd")[-1]]
        anime_data["description"] = description.get_text(" ", strip=True) if description else None
        anime_data["thumbnail"] = thumbnail["srcset"].rstrip(" 2x") if thumbnail else None
        anime_data["screenshots"] = screenshots if screenshots else None
        anime_data["trailer"] = trailer["href"] if trailer else None
        
        formatted_anime_data = self._data_formatted(anime_data)
        
        logging.debug(f"Anime data: {anime_data}")
        logging.debug(f"Formatted anime data: {formatted_anime_data}")
        
        self.anime_data_list.append(formatted_anime_data)
        
        progress.advance(task_id, 1)

    async def fetch_anime_preview_info(self, page: int, progress: Progress, task_id: int) -> None:
        url = f"https://animego.org/anime?page={page}"
        while True:
            headers = {"user-agent": self.get_user_agent()}
            try:
                response = await self.client.get(url, headers=headers)
                logging.debug(f"Processing page: {page} | Status code: {response.status_code}")
                
                if response.status_code == 200:
                    break
                else:
                    await asyncio.sleep(uniform(1, 5))
            except Exception as ex:
                await asyncio.sleep(uniform(1, 5))
        
        soup = BeautifulSoup(response.text, "lxml")
        anime_container = soup.select("#anime-list-container > .col-12")
        for i, column in enumerate(anime_container, 1):            
            genres = self.check_if_text_exists(column, ".anime-genre")
            anime_preview_info = {
                "id": (page - 1) * 20 + i,
                "title": self.check_if_text_exists(column, ".h5"),
                "synonyms": self.check_if_text_exists(column, ".small.mb-2"),
                "type": self.check_if_text_exists(column, ".mb-2 > span"),
                "season": self.check_if_text_exists(column, ".anime-year"),
                "genre": [genre for genre in genres.split(",")] if genres else None,
                "short_description": self.check_if_text_exists(column, ".description"),
                "url": column.select_one(".h5").next.get("href")
            }
            self.anime_preview_list.append(anime_preview_info)
            logging.debug(f"Added {anime_preview_info['title']}")
        
        progress.advance(task_id, 1)

    async def fetch_all_anime_data(self) -> None:
        with open("anime_previews.json", "r", encoding="utf-8") as file:
            urls = [item["url"] for item in json.load(file)]
        
        try:
            with Progress(console=self.console) as progress:
                task_id = progress.add_task(
                    "[white]Fetching anime data ::", 
                    total=len(urls)
                )
                tasks = []
                for i, url in enumerate(urls, 1):
                    task = self.fetch_anime_data(url, i, progress, task_id)
                    tasks.append(task)
                await asyncio.gather(*tasks)
        finally:
            await self.client.aclose()
        
        if len(self.anime_data_list) >= 2361:
            logging.info("Fetching anime data process completed successfully")
            self._save_anime_data()
        elif len(self.anime_data_list) < 2361:
            logging.info(f"Fetching anime data process completed unsuccessfully | {len(self.anime_data_list)}/2361")
            self._save_anime_data()
        else:
            logging.info("Operation aborted. Сompleted unsuccessfully")

    async def fetch_all_anime_previews(self) -> None:
        total_pages = 119
        try:
            with Progress(console=self.console) as progress:
                task_id = progress.add_task(
                    "[white]Fetching anime previews info ::", 
                    total=total_pages
                )
                tasks = [
                    self.fetch_anime_preview_info(
                        page, progress, task_id
                    )
                    for page in range(1, total_pages + 1)
                ]
                await asyncio.gather(*tasks)
        finally:
            await self.client.aclose()
        
        if len(self.anime_preview_list) >= 2361:
            logging.info("Fetching anime previews process completed successfully")
            self._save_anime_previews()
        else:
            logging.info("Operation aborted. Сompleted unsuccessfully")

    def _save_anime_data(self) -> None:
        data = sorted(self.anime_data_list, key=lambda item: item["id"])
        with open("anime_data.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        logging.info(f"Anime data is saved in \"anime_data.json\"")

    def _save_anime_previews(self) -> None:
        data = sorted(self.anime_preview_list, key=lambda item: item["id"])
        with open("anime_previews.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        logging.info(f"Anime previews data is saved in \"anime_previews.json\"")
    
    def _data_formatted(self, data: dict) -> dict:
        formatted_data = data
        
        for key in data.keys():
            if key in ("characters", "id"):
                continue
            
            value = data.get(key)
            if value is not None and " , " in value:
                formatted_data[key] = value.split(" , ")
            
        characters = data.get("characters")
        formatted_characters = []
        for part in characters:
            if "озвучивает" in part:
                parts = re.split(r'\(озвучивает\s+(.*?)\)', part)
                formatted_characters.append({parts[0].strip(): parts[1].rstrip(" )").strip()})
            else:
                formatted_characters.append(part)
        formatted_data["characters"] = formatted_characters
        
        return formatted_data
    
    def _translate(self, in_text: str) -> str:
        translation_map = {
            "Следующий эпизод": "next_episode",
            "Тип": "type",
            "Эпизоды": "episodes",
            "Статус": "status",
            "Жанр": "genre",
            "Первоисточник": "source",
            "Выпуск": "release_date",
            "Студия": "studio",
            "Рейтинг MPAA": "mmpa_rating",
            "Возрастные ограничения": "age_restrictions",
            "Длительность": "duration",
            "Озвучка": "voiceover",
            "Снят по манге": "manga",
            "Главные герои": "characters",
            "Автор оригинала": "author",
            "Режиссёр": "director",
            "Сезон": "season"
        }
        return translation_map.get(in_text, in_text)

    @staticmethod
    def check_if_text_exists(soup: BeautifulSoup, selector: str) -> str:
        element = soup.select_one(selector)
        if not element:
            return None
        return element.get_text(strip=True)
    
    @staticmethod    
    def get_user_agent() -> str:
        return choice(config.user_agents)