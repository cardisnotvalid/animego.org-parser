# Parser AnimeGO.org

Скрипт использует асинхронные запросы для парсинга подробной информации по каждому аниме, доступному на веб-сайте. Полученные данные сохраняются в формате JSON.

## Пример JSON файлов:

**anime_previews.json**:

```
{
    "id": 1,
    "title": "Вечера с кошкой 2",
    "synonyms": "Yoru wa Neko to Issho Season 2",
    "type": "ONA",
    "season": "2023",
    "genre": [
        "Комедия"
    ],
    "short_description": "Второй сезон.",
    "url": "https://animego.org/anime/vechera-s-koshkoy-2-2373"
}
```

**anime_data.json**:

```
{
    "id": 1,
    "title": "Вечера с кошкой 2",
    "synonyms": [
        "Yoru wa Neko to Issho Season 2",
        "Nights with a Cat",
        "夜は猫といっしょ Season2",
        "Zutto Neko Shoshinsha"
    ],
    "next_episode": "26 июл. 2023 ср 14:00 ожидается выход 19 серии",
    "type": "ONA",
    "episodes": "18 / ?",
    "genre": "Комедия",
    "source": "Веб-манга",
    "release_date": "8 марта 2023",
    "studio": "Studio Puyukai",
    "age_restrictions": "16+",
    "duration": "2 мин. ~ серия",
    "voiceover": "Dream Cast",
    "manga": "Вечера с кошкой",
    "characters": [
        {
            "Фута": "Сатоси Хино"
        },
        {
            "Кюруга": "Аяхи Такагаки"
        },
        {
            "Пи": "Ацуми Танэдзаки"
        }
    ],
    "description": "Второй сезон.",
    "thumbnail": "https://animego.org/media/cache/thumbs_500x700/upload/anime/images/64b03c7e009e7928343687.jpg",
    "screenshots": null,
    "trailer": null
}
```