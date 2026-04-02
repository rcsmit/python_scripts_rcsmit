# 🐍 python_scripts_rcsmit

> **A workshop floor of standalone Python scripts** — experiments, utilities, scrapers, games, visualisations and one-off tools by [René Smit](https://rene-smit.com).

**GitHub → [github.com/rcsmit/python_scripts_rcsmit](https://github.com/rcsmit/python_scripts_rcsmit)**  
**Interactive apps → [rcsmit.streamlit.app](https://rcsmit.streamlit.app)**

---

Unlike the Streamlit portfolio, this repo is the *workshop floor* — scripts that run locally, produce output files, prototype ideas, or do things that don't need a browser. Some became Streamlit apps later. Some are just here for reference.

---

## 📁 Folders

| Folder | Contents |
|---|---|
| [`cartopy_fun/`](cartopy_fun/) | Map visualisations using Cartopy |
| [`extras/`](extras/) | Miscellaneous helper scripts |
| [`facebookfriends_on_map/`](facebookfriends_on_map/) | Plot Facebook friends on a world map |
| [`helpers/`](helpers/) | Reusable utility functions |
| [`input/`](input/) | Data input files used by scripts |
| [`quotes_app/`](quotes_app/) | Quote collection & display app |
| [`unsorted/`](unsorted/) | Overflow — things that haven't found a home yet |
| [`warmingstripes/`](warmingstripes/) | Climate warming stripe visualisations |

---

## 🗺️ Maps & Geo

| Script | What it does |
|---|---|
| [`geocode.py`](geocode.py) | Geocode addresses to lat/lon coordinates |
| [`geocode2.py`](geocode2.py) | Alternative geocoding approach |
| [`googlemap_to_maperitive.py`](googlemap_to_maperitive.py) | Convert Google Maps data for use in Maperitive |
| [`netherlands_landcover_map.py`](netherlands_landcover_map.py) | 3D isometric land cover map of the Netherlands using ESA WorldCover satellite data + rasterio |
| [`heatmap_.py`](heatmap_.py) | Generate a geographic heatmap from coordinate data |

---

## 📊 Data & Analysis

| Script | What it does |
|---|---|
| [`correlationmatrix.py`](correlationmatrix.py) | Generate a correlation matrix from tabular data |
| [`steekproefgrootte.py`](steekproefgrootte.py) | Sample size calculator for statistical significance |
| [`testhalveringstijd.py`](testhalveringstijd.py) | Half-life / exponential decay calculator |
| [`random_vs_binairy_search.py`](random_vs_binairy_search.py) | Visual comparison of random vs binary search performance |
| [`runninganalyse.py`](runninganalyse.py) | Running/sport data analysis |
| [`bezetting_per_jaar.csv.csv`](bezetting_per_jaar.csv.csv) | Occupancy data per year (input file) |
| [`lange_lijst_naar_kolommen.py`](lange_lijst_naar_kolommen.py) | Reshape a long list into columns |
| [`add_categories_mastersheet.py`](add_categories_mastersheet.py) | Add category labels to a master finance sheet |
| [`testduplicates.py`](testduplicates.py) | Find and flag duplicate rows in a dataset |
| [`testinterval.py`](testinterval.py) | Interval/confidence interval experiments |
| [`proteine_intake_vegans.py`](proteine_intake_vegans.py) | Protein intake calculator for vegans |

---

## 🤖 AI & Image

| Script | What it does |
|---|---|
| [`calculate_beauty_from_image.py`](calculate_beauty_from_image.py) | Compute Golden Ratio facial proportions from a photo |
| [`get_landmark_coordinates_from_image.py`](get_landmark_coordinates_from_image.py) | Extract facial landmark coordinates from an image |
| [`face_recognition_test.py`](face_recognition_test.py) | Face recognition experiments |
| [`flux_schnell_image_ai.py`](flux_schnell_image_ai.py) | Generate images with Flux Schnell AI model |
| [`open_ai_play.py`](open_ai_play.py) | OpenAI API playground experiments |
| [`read_txt_from_imge_on_clipboard.py`](read_txt_from_imge_on_clipboard.py) | OCR: extract text from an image on the clipboard |
| [`read_txt_in_images.py`](read_txt_in_images.py) | OCR: read text from image files |
| [`show_txt_in_images.py`](show_txt_in_images.py) | Overlay extracted text onto images |
| [`lyrics_to_images.py`](lyrics_to_images.py) | Render song lyrics as image files |

---

## 🌐 Web, Scraping & APIs

| Script | What it does |
|---|---|
| [`scrape_google_reviews.py`](scrape_google_reviews.py) | Scrape Google Maps reviews for a venue |
| [`scrape_excel.py`](scrape_excel.py) | Scrape tabular data from a webpage into Excel |
| [`email_extractor.py`](email_extractor.py) | Extract email addresses from text or web pages |
| [`read_NRC.py`](read_NRC.py) | Parse and read NRC newspaper articles |
| [`read_and_translate_pdf.py`](read_and_translate_pdf.py) | Read a PDF and auto-translate its content |
| [`read_conversations_json.py`](read_conversations_json.py) | Parse ChatGPT `conversations.json` export |
| [`pytube_testq1.py`](pytube_testq1.py) | Download YouTube videos with pytube |
| [`get_forex_data.py`](get_forex_data.py) | Fetch forex exchange rate data |
| [`download_knmi_neerslag.py`](download_knmi_neerslag.py) | Download KNMI precipitation station data |
| [`fritsander_api_knmi.py`](fritsander_api_knmi.py) | Fetch KNMI data via Frits Ander's API wrapper |
| [`garmin_connect.py`](garmin_connect.py) | Pull activity data from Garmin Connect |
| [`speedtest.py`](speedtest.py) | Run an internet speed test from the command line |

---

## 💬 Telegram Bots

| Script | What it does |
|---|---|
| [`telegram_first_bot.py`](telegram_first_bot.py) | A first "hello world" Telegram bot |
| [`telegram_echobot.py`](telegram_echobot.py) | Telegram bot that echoes messages back |
| [`telegram_google_translate.py`](telegram_google_translate.py) | Telegram bot that translates messages via Google Translate |

---

## 🎮 Games & Fun

| Script | What it does |
|---|---|
| [`caspargame2.py`](caspargame2.py) | A simulation of a game in Caspar (café in Arnhem, NL) |
| [`leelagame.py`](leelagame.py) | Digital version of the Leela (Hindu board game of life) |
| [`leelamarkov.py`](leelamarkov.py) | Markov chain text generation from Leela game descriptions |
| [`leela scipython elegant.py`](<leela scipython elegant.py>) | Elegant SciPython version of the Leela game |
| [`sudoku.py`](sudoku.py) | Sudoku solver |
| [`mandelbrot1.py`](mandelbrot1.py) | Mandelbrot set visualisation |
| [`steve_balmer_number_game.py`](steve_balmer_number_game.py) | A number guessing game |
| [`snakes natalino busso.py`](<snakes natalino busso.py>) | Snake game implementation |
| [`gymcode.py`](gymcode.py) | Gym code/workout tracker |
| [`lootjes_trekken.py`](lootjes_trekken.py) | Secret Santa draw — assign random pairs without conflicts |
| [`conspiracy.py`](conspiracy.py) | Conspiracy theory generator |
| [`randomnumber.py`](randomnumber.py) | Random number experiments |

---

## 🔤 Text & Language

| Script | What it does |
|---|---|
| [`jumble.py`](jumble.py) | Word jumble / anagram puzzle generator |
| [`simple_wordcloud.py`](simple_wordcloud.py) | Generate a word cloud from any text |
| [`speak_to_me.py`](speak_to_me.py) | Text-to-speech: reads text aloud |
| [`text2columns.py`](text2columns.py) | Split a text column into multiple columns |
| [`findspaces.py`](findspaces.py) | Find and fix irregular spacing in text files |
| [`csv_to_json.py`](csv_to_json.py) | Convert a CSV file to JSON format |
| [`makesublists.py`](makesublists.py) | Split a list into evenly-sized sublists |

---

## 🖼️ Visualisation & Graphics

| Script | What it does |
|---|---|
| [`svg_turtle.py`](svg_turtle.py) | Draw SVG graphics using turtle-style commands |
| [`svg_turtle_test.py`](svg_turtle_test.py) | Tests and experiments for SVG turtle drawing |
| [`fen_to_svg.py`](fen_to_svg.py) | Convert a chess FEN string to an SVG board diagram |
| [`plot_pylustrator.py`](plot_pylustrator.py) | Interactive plot editing with Pylustrator |
| [`screenshot_every_second.py`](screenshot_every_second.py) | Take a screenshot every second (timelapse / monitoring) |

---

## 💰 Finance & Utilities

| Script | What it does |
|---|---|
| [`inkomstenbelasting.py`](inkomstenbelasting.py) | Dutch income tax calculator (standalone, no UI) |
| [`kassabon.py`](kassabon.py) | Receipt / till receipt reader |
| [`business_days.py`](business_days.py) | Calculate the number of business days between two dates |
| [`datetime_timedelta_codesnippets.py`](datetime_timedelta_codesnippets.py) | Reference snippets for datetime and timedelta operations |
| [`play_with_copy.py`](play_with_copy.py) | Experiments with Python's copy / deepcopy behaviour |
| [`clear_cache_test.py`](clear_cache_test.py) | Test and benchmark cache clearing strategies |
| [`ding.py`](ding.py) | Play a notification sound |

---

## 🔑 Config & Setup

| File | Purpose |
|---|---|
| [`.env.example`](.env.example) | Template for environment variables (API keys, paths) |
| [`keys_dummy.py`](keys_dummy.py) | Dummy keys file — copy and fill in your own secrets |
| [`database_file_name`](database_file_name) | Stores the path to the SQLite database |

---

## Running a script

Most scripts are self-contained. Clone the repo and run:

```bash
git clone https://github.com/rcsmit/python_scripts_rcsmit
cd python_scripts_rcsmit
pip install -r requirements.txt   # if present, or install deps per script
python script_name.py
```

Scripts that need API keys expect either a `.env` file (copy `.env.example`) or a populated `keys_dummy.py`.

---

## Related

| Repo | What's there |
|---|---|
| [streamlit_scripts](https://github.com/rcsmit/streamlit_scripts) | 79 interactive browser apps — [live at rcsmit.streamlit.app](https://rcsmit.streamlit.app) |
| [covid19](https://github.com/rcsmit/COVIDcases) | Dutch COVID-19 excess mortality analysis |

---

## Stack

Python 3 · pandas · matplotlib · Plotly · Cartopy · rasterio · BeautifulSoup · OpenCV · pytube · python-telegram-bot · OpenAI API

---

## 👤 About

I'm René Smit — a Dutch multidisciplinary freelancer with a nomadic lifestyle across Da Nang, Chiang Mai, Bali, and the Netherlands.  
I am available for freelance data analysis & visualisation projects, Python/Streamlit development, financial coaching & planning,  graphic & web design, and consultancy for hospitality & tourism businesses.

🌐 [rene-smit.com](https://rene-smit.com) · 📊 [rcsmit.streamlit.app](https://rcsmit.streamlit.app) · 🐙 [github.com/rcsmit](https://github.com/rcsmit)

---

## License

All scripts are provided as-is for educational and personal use.  
© René Smit — [rene-smit.com](https://rene-smit.com) · [github.com/rcsmit](https://github.com/rcsmit)
