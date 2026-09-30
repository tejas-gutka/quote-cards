# quote-cards

Image cards for weekly quotes.

- `cards/` – card images used in scheduled Buffer posts. Buffer fetches each image when its post publishes, so a card must stay here until then.
- `scripts/generate_card.py` – makes a card: `python scripts/generate_card.py --quote "..." --author "..." --output cards/card_qtXXX_day.png`
- `scripts/fonts/` – DejaVu fonts used on the cards (free licence, see DejaVu-LICENSE.txt).

No keys or tokens are ever stored in this folder – it is public.
