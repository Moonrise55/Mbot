A discord bot with tools and automatic puzzlehunt progress tracking for a small team. For fun, the bot is named after a character from the works of Brandon Sanderson.

### Toolbox 
* `!nu`: [Nutrimatic](https://nutrimatic.org/) for anagrams, regex search, patterns, etc
* ~~`!qq`: [Quipqiup](https://quipqiup.com/) cryptograms~~ TODO: update to beta3 version of site
* `!cc`: Caesar shift 
* `!alpha`: Alphanumeric A1Z26
* `!atom`: Periodic table
* `!atbash`: Atbash cipher
* `!v`: Vigenere cipher

### Puzzle Manager
Puzzle progress stored in a master "Nexus" google sheet.
* With one puzzle `!create` command: create channel, duplicate template google sheet, update nexus sheet, send links to discord server
* Log answer in nexus sheet with `!solve`
*  Store and view `!login` info for team
*  View puzzle progress in `!nexus`
*  Store common resources in `!tag`

Example of auto-generated nexus sheet (answers removed)
![example](https://github.com/Moonrise55/Mbot/blob/master/misc/nexus_example.PNG)

### Bot setup
1. Create a `.env` with your bot token and postgreSQL database address.
```
DISCORD_TOKEN= ...   # your discord bot token
DATABASE_URL= ...     # address as postgres:yourdbconnectionURI
GOOGLE_CLIENT_SECRETS=...   # google service account credentials
```
Database connection needed for the puzzle manager only. Additionally, you would need to:

2. Enable Google API following instructions on [gspread documentation](https://gspread.readthedocs.io/en/latest/oauth2.html#for-bots-using-service-account) to get a `client_secrets.json` for a service account.
3. Run `python3.6 db_launcher.py` to setup some simple db tables and hope nothing breaks.
4. Set up a google folder (shared w/ service account address) with Nexus and Puzzle Template sheets. 



