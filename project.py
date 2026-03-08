import argparse
import sqlite3
from helpers import create_connection, execute_query, execute_read_query, fetch_response, confirm, shutdown
import urllib.parse
from progress.bar import ChargingBar
import re
import sys
from tabulate import tabulate
from termcolor import colored

class dota():
    # Customization of the group of roles that each hero belongs to.
    # 'c' for Carry, 's' for Support, 'm' for Mid and 'o' for Offlane
    HERO_GROUP = {'anti-mage': ('c', 'm'), 'abaddon': ('o', 's'), 'ancient-apparition': ('s',), 'alchemist': ('m', 'c'),
                  'arc-warden': ('m', 'c'), 'axe': ('o', 'm'), 'bane': ('s',), 'batrider': ('m',), 'beastmaster': ('o',),
                  'bloodseeker': ('o', 'm', 'c'), 'bounty-hunter': ('m', 's'), 'brewmaster': ('o',), 'bristleback': ('o', 'm', 'c'),
                  'broodmother': ('m',), 'centaur-warrunner': ('o', 'm'), 'chaos-knight': ('c', 'o', 'm'), 'chen': ('s',),
                  'clinkz': ('c', 'm'), 'clockwerk': ('s', 'o'), 'crystal-maiden': ('s',), 'dark-seer': ('o',), 'dark-willow': ('s',),
                  'dawnbreaker': ('c', 'm', 'o'), 'dazzle': ('s',), 'death-prophet': ('m', 'o'), 'disruptor': ('s',),
                  'doom': ('m', 'o'), 'dragon-knight': ('c', 'm', 'o'), 'drow-ranger': ('c', 'm'), 'earth-spirit': ('s',),
                  'earthshaker': ('s', 'm', 'o', 'c'), 'elder-titan': ('s',), 'ember-spirit': ('m', 'c'), 'enchantress': ('m', 'o', 's'),
                  'enigma': ('o', 's'), 'faceless-void': ('c',), 'grimstroke': ('s',), 'gyrocopter': ('s', 'c', 'm', 'o'),
                  'hoodwink': ('s',), 'huskar': ('c', 'm', 'o'), 'invoker': ('m', 's'), 'io': ('s',), 'jakiro': ('s',),
                  'juggernaut': ('c', 'm'), 'keeper-of-the-light': ('s',), 'kunkka': ('o', 'm'), 'legion-commander': ('o', 'm', 'c'),
                  'leshrac': ('m', 'o', 'c'), 'lich': ('s',), 'lifestealer': ('c',), 'lina': ('c', 'm', 's'), 'lion': ('s',),
                  'lone-druid': ('c', 'm'), 'luna': ('c',), 'lycan': ('c', 'm', 'o'), 'magnus': ('o', 'm'), 'marci': ('o', 'm', 's'),
                  'mars': ('o', 'm'), 'medusa': ('c'), 'meepo': ('m',), 'mirana': ('m', 's'), 'monkey-king': ('m', 'c'),
                  'morphling': ('m', 'c'), 'naga-siren': ('c', 'o', 'm'), 'natures-prophet': ('c', 'm', 'o'), 'necrophos': ('c', 'm', 'o'),
                  'night-stalker': ('m', 'o'), 'nyx-assassin': ('s',), 'ogre-magi': ('m', 'o', 's'), 'omniknight': ('s', 'o'),
                  'oracle': ('s',), 'outworld-destroyer': ('c', 'm'), 'pangolier': ('o', 'm'), 'phantom-assassin': ('c',),
                  'phantom-lancer': ('c',), 'phoenix': ('o', 's'), 'primal-beast': ('o', 'm'), 'puck': ('m',), 'pudge': ('c', 'm', 'o'),
                  'pugna': ('m', 's'), 'queen-of-pain': ('m', 's', 'o'), 'razor': ('m', 'o', 'c'), 'riki': ('c', 'm'),
                  'rubick': ('m', 's'), 'sand-king': ('m', 'o'), 'shadow-demon': ('s',), 'shadow-fiend': ('m', 'c'),
                  'shadow-shaman': ('s',), 'silencer': ('m', 's', 'c'), 'skywrath-mage': ('s', 'm'), 'slardar': ('o', 'c'),
                  'slark': ('m',), 'snapfire': ('s',), 'sniper': ('m', 'c'), 'spectre': ('c',), 'spirit-breaker': ('m', 'o', 's'),
                  'storm-spirit': ('m',), 'sven': ('c', 'm'), 'techies': ('m', 's'), 'templar-assassin': ('c', 'm'), 'terrorblade': ('c',),
                  'tidehunter': ('o', 'm'), 'timbersaw': ('o', 'm'), 'tinker': ('m',), 'tiny': ('m', 'o'), 'treant-protector': ('s',),
                  'troll-warlord': ('m', 'c'), 'tusk': ('m', 'c', 's'), 'underlord': ('o',), 'undying': ('o', 's'), 'ursa': ('c',),
                  'vengeful-spirit': ('m', 's', 'o'), 'venomancer': ('s', 'm', 'o'), 'viper': ('c', 'm', 's', 'o'), 'visage': ('m', 'o'),
                  'void-spirit': ('m', 'o'), 'warlock': ('s',), 'weaver': ('m', 'c', 'o', 's'), 'windranger': ('m', 'o', 'c'),
                  'winter-wyvern': ('m', 's'), 'witch-doctor': ('s',), 'wraith-king': ('c',), 'zeus': ('m', 's')}
    
    # Customization of aliases for each hero. Add your own aliases too! Format: {'alias': 'hero_name'}
    HERO_ALIAS = {'aba': 'abaddon', 'alch': 'alchemist', 'aa': 'ancient-apparition', 'am': 'anti-mage', 'arc': 'arc-warden', 'bat':'batrider',
                  'beast': 'beastmaster', 'bs': 'bloodseeker', 'bh': 'bounty-hunter', 'brew': 'brewmaster', 'bb': 'bristleback',
                  'brood': 'broodmother', 'centaur': 'centaur-warrunner', 'ck': 'chaos-knight', 'clock': 'clockwerk', 'cw': 'clockwerk', 'cm': 'crystal-maiden',
                  'ds': 'dark-seer', 'dw': 'dark-willow', 'dawn': 'dawnbreaker', 'daz': 'dazzle', 'dp': 'death-prophet', 'dis': 'disruptor',
                  'dk': 'dragon-knight', 'drow': 'drow-ranger', 'es': 'earth-spirit', 'earth': 'earth-spirit', 'shaker': 'earthshaker',
                  'et': 'elder-titan', 'ember': 'ember-spirit', 'ench': 'enchantress', 'enig': 'enigma', 'void': 'faceless-void',
                  'grim': 'grimstroke', 'gyro': 'gyrocopter', 'hood': 'hoodwink', 'hus': 'huskar', 'invo': 'invoker', 'jak':'jakiro',
                  'jugg': 'juggernaut', 'kotl': 'keeper-of-the-light', 'coco': 'kunkka', 'lc': 'legion-commander', 'lesh': 'leshrac',
                  'ls': 'lifestealer', 'druid': 'lone-druid', 'lyc': 'lycan', 'mag': 'magnus', 'med': 'medusa', 'mira': 'mirana',
                  'mk': 'monkey-king', 'morph': 'morphling', 'naga': 'naga-siren', 'np': 'natures-prophet', 'nec': 'necrophos',
                  'ns': 'night-stalker', 'nyx': 'nyx-assassin', 'ogre': 'ogre-magi', 'om': 'ogre-magi', 'omni': 'omniknight',
                  'ok': 'omniknight', 'ora': 'oracle', 'od': 'outworld-destroyer', 'pango': 'pangolier', 'pa': 'phantom-assassin',
                  'pl': 'phantom-lancer', 'pb': 'primal-beast', 'qop': 'queen-of-pain', 'rub': 'rubick', 'sk': 'sand-king',
                  'sd': 'shadow-demon', 'sf': 'shadow-fiend', 'shaman': 'shadow-shaman', 'ss': 'shadow-shaman', 'silen': 'silencer',
                  'sky': 'skywrath-mage', 'slard': 'slardar', 'snap': 'snapfire', 'spe': 'spectre', 'sb': 'spirit-breaker',
                  'storm': 'storm-spirit', 'tech': 'techies', 'ta': 'templar-assassin', 'tb': 'terrorblade', 'tide': 'tidehunter',
                  'timber': 'timbersaw', 'tk': 'tinker', 'treant': 'treant-protector', 'troll': 'troll-warlord', 'under': 'underlord',
                  'ud': 'undying', 'vs': 'vengeful-spirit', 'venom': 'venomancer', 'vis': 'visage', 'vos': 'void-spirit', 'wea': 'weaver',
                  'wr': 'windranger', 'ww': 'winter-wyvern', 'wd': 'witch-doctor', 'wk': 'wraith-king'}

    # A manual hero total count for checking database integrity
    HERO_TOTAL = 123
    
    # The key word to define the timeliness of data that will be fetched when in --update mode: 'week' - fetch data from last week, 'month' - fetch data from last month,
    # '3month' - fetch data from last 3 months.
    # Default - empty string - uses 'month'
    DATA_DATE = 'patch_7.32'
    
    db = create_connection("dota.db")
    cursor = db.cursor()
    
    
    @classmethod
    def update_data(cls):
        with ChargingBar('Rebuilding database...', max=8) as bar:
            create_heroes = """
            CREATE TABLE IF NOT EXISTS heroes (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );
            """
            create_hero_counter = """
            CREATE TABLE IF NOT EXISTS hero_counter (
                id_hero INTEGER,
                id_counter_hero INTEGER,
                advantage FLOAT,
                PRIMARY KEY (id_hero, id_counter_hero)
            );
            """
            execute_query(cls.cursor, "DROP TABLE IF EXISTS heroes;")
            bar.next()
            execute_query(cls.cursor, "DROP TABLE IF EXISTS hero_counter;")
            bar.next()
            execute_query(cls.cursor, "DROP INDEX IF EXISTS id_index;")
            bar.next()
            execute_query(cls.cursor, "DROP INDEX IF EXISTS name_index;")
            bar.next()
            execute_query(cls.cursor, "DROP INDEX IF EXISTS id1_index;")
            bar.next()
            execute_query(cls.cursor, "DROP INDEX IF EXISTS id2_index;")
            bar.next()
            execute_query(cls.cursor, create_heroes)
            bar.next()
            execute_query(cls.cursor, create_hero_counter)
            bar.next()
        
        bar = ChargingBar("Updating hero records...", max=cls.HERO_TOTAL)
        if heroes_response := fetch_response("https://api.opendota.com/api/heroes").json():
            hero_num = len(heroes_response)
            
            # Quit the program with an error report if the total hero count of the retrived data doesn't equal HERO_TOTAL
            if hero_num != cls.HERO_TOTAL:
                sys.exit(f"Error: hero total count from retrived data ({hero_num}) not consistent with class constant HERO_TOTAL ({cls.HERO_TOTAL}). Please double check the total number of all heroes before proceeding with the update")
                
            #Insert into hero table all hero ids and names from OpenDota API
            for hero in heroes_response:
                execute_query(cls.cursor, "INSERT INTO heroes (id, name) VALUES (?, ?);", 
                            int(hero["id"]), cls.name_format(hero['localized_name']))
                bar.next()
            bar.finish()
                    
            failed = 0
            with ChargingBar("Updating hero matchup data...", max=hero_num*(hero_num-1)) as bar:
                
                for hero in heroes_response:
                    hero_name = cls.name_format(hero['localized_name'])
                    
                    
                    if not cls.update_matchup_records(hero_name, bar):
                        print(f"Failed to update matchup data of {hero_name}")
                        failed += 1
                        bar.next(hero_num-1)
                        
                execute_query(cls.cursor, "CREATE INDEX IF NOT EXISTS id_index ON heroes (id);")
                execute_query(cls.cursor, "CREATE INDEX IF NOT EXISTS name_index ON heroes (name);")
                execute_query(cls.cursor, "CREATE INDEX IF NOT EXISTS id1_index ON hero_counter (id_hero);")
                execute_query(cls.cursor, "CREATE INDEX IF NOT EXISTS id2_index ON hero_counter (id_counter_hero);")
            print(f"{hero_num - failed} hero records successfully updated!")
            if not cls.check_database_integrity():
                print(colored("Warning: the database is still not integrated, try to update the database again or \n\t  insert absent hero records manually with [--hero HERO] option", 'red'))
        else:
            print("Failed to connect to hero information, please check your internet connection and try again")
       
    @classmethod     
    def parse_counter_response(cls, response):
        '''
            Parse a text file of response from DotaBuff.com into a dictionary that stores hero counters
        '''
        value_finder = r'<tr data-link-to="\/heroes\/(.+?)"><td.+?<\/td><td.+?<\/td><td data-value="(.+?)"'
        matches = re.finditer(value_finder, response)
        try:
            counter_dict = {match.group(1): -float(match.group(2)) for match in matches}
        except IndexError:
            raise ValueError("Did not find 2 subgroups in the match object")
        else:
            return counter_dict
        
    @classmethod
    def update_matchup_records(cls, hero, bar=None):
        '''
            A method to update the matchup records of a specific hero, by deleting old records and then inserting new records.
            parameter hero: formatted name of the hero to update.
            return: True if successful, and false if failed.
        '''
        try:
            hero_id = cls.name_to_id(hero)
        except ValueError:
            print(f"Error: Hero id not found for {hero}")
            return False
        
        retry = 3
        if cls.DATA_DATE:
            url = f"https://www.dotabuff.com/heroes/{urllib.parse.quote_plus(hero)}/counters?date={urllib.parse.quote_plus(cls.DATA_DATE)}"
        else:
            url = f"https://www.dotabuff.com/heroes/{urllib.parse.quote_plus(hero)}/counters"
        while retry > 0:
            if hero_counter_response := fetch_response(url, {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'}):
                #parse text response into dictionary of lowered hero name with hyphens in between
                if retry < 3:
                    print(f"\nSuccessfully retrieved matchup data of hero {hero}")
                hero_counter_dict = cls.parse_counter_response(hero_counter_response.text)  
                if len(hero_counter_dict) != 122:
                    print(f"\nError: Did not find 122 counter heroes in the response. Found {len(hero_counter_dict)} instead")
                    return False
                else:
                    try:
                        execute_query(cls.cursor, "DELETE FROM hero_counter WHERE id_hero = ?", hero_id)
                    except sqlite3.Error as e:
                        print(f"\nA database error occurred trying to update hero matchup record: {e}")
                        return False
                    # Inserting counter information against all other heroes
                    for counter in hero_counter_dict:
                        try:
                            execute_query(cls.cursor, "INSERT INTO hero_counter (id_hero, id_counter_hero, advantage) VALUES (?, ?, ?);"
                                    , hero_id, cls.name_to_id(counter), hero_counter_dict[counter])
                        except sqlite3.Error as e:
                            print(f"\nA database error occurred trying to update hero matchup record: {e}")
                            return False
                        if bar:
                            bar.next()
                    return True
            else:
                if retry > 1:
                    print(f"Failed to get response of hero_counter {hero}, trying again...", )
                elif retry <= 1:
                    print(f"Failed to get response of hero_counter {hero}, try to run the program with argument --update --hero HERO_NAME to manually update {hero}'s matchup data later")
                    print(f"Skipping to the next hero...")
                    return False
                retry -= 1
                
        
    @classmethod
    def name_to_id(cls,name):
        if result := execute_read_query(cls.cursor, "SELECT id FROM heroes WHERE name = ?", cls.name_format(name)):
            return result[0][0]
        else:
            raise ValueError(f"Did not find hero name {name} in database")
    
    @classmethod
    def id_to_name(cls, id):
        if result := execute_read_query(cls.cursor, "SELECT name FROM heroes WHERE id = ?", id):
            return result[0][0]
        else:
            raise ValueError(f"Did not find id {id} in database")
            
    @classmethod
    def name_format(cls, name):
        return name.lower().replace(" ", "-").replace("'", "")
    
    @classmethod
    def alias(cls, short):
        return cls.HERO_ALIAS.get(short.lower(), short)
    
    @classmethod
    #check if a hero name or alias is valid and is present in the database
    def authenticate(cls, hero: str):
        hero = hero.lower().strip()
        hero = cls.alias(hero)
        hero = cls.name_format(hero)
        if execute_read_query(cls.cursor, "SELECT id FROM heroes WHERE name = ?", hero):
            return hero
        else:
            return ""
    
    @classmethod
    #check if the database has information for all heroes
    def check_database_integrity(cls):
        
        try:
            # Check records of heroes and hero_counter
            if len(execute_read_query(cls.cursor, "SELECT * FROM heroes;")) != cls.HERO_TOTAL:
                return False
            if len(execute_read_query(cls.cursor, "SELECT * FROM hero_counter;")) != (cls.HERO_TOTAL) * (cls.HERO_TOTAL - 1):
                return False
            
            # Check if indexes have been created
            if len(execute_read_query(cls.cursor, "SELECT * FROM sqlite_master WHERE type = 'index' AND (name='id_index' OR name='name_index' OR name='id1_index' OR name='id2_index');")) != 4:
                return False
            
        except sqlite3.Error:
            return False

        return True
        
    @classmethod
    def utility_check(cls):
        '''
            check if the names in the customized class constants -- HERO_GROUP and HERO_ALIAS are valid
        '''
        error = 0
        hero_names = list(map(lambda a: a[0], execute_read_query(cls.cursor, "SELECT name FROM heroes;")))
        
        # Validation for HERO_GROUP constant
        n = len(cls.HERO_GROUP)
        if n > cls.HERO_TOTAL:
            print(f"HERO_GROUP validation report: {n - cls.HERO_TOTAL} excessive heroes listed")
            error += 1
        for hero in hero_names:
            if hero not in cls.HERO_GROUP:
                print(f"HERO_GROUP validation report: {hero} is missing from the list")
                error += 1
        
        for hero in cls.HERO_GROUP:
            if hero not in hero_names:
                print(f"HERO_GROUP validation report: name {hero} in HERO_GROUP is not a valid hero name")
                error += 1
            if not isinstance(cls.HERO_GROUP[hero], tuple):
                print(f"HERO_GROUP validation report: value of hero {hero} {cls.HERO_GROUP[hero]} is not a valid data type: must be a tuple")
                error += 1
            else:
                for i in cls.HERO_GROUP[hero]:
                    if i not in ['c', 'm', 'o', 's']:
                        print(f"HERO_GROUP Validation report: unrecognized role indicator in the group definition of hero {hero}: {i}")
                        error += 1
            
        # Validation for HERO_ALIAS constant
        for alias in cls.HERO_ALIAS:
            if cls.name_format(cls.HERO_ALIAS[alias]) not in hero_names:
                print(f"HERO_ALIAS Validation report: alias {alias} points to an unrecognized hero name: {cls.HERO_ALIAS[alias]}")
                error += 1
            
        if error == 0:
            print(colored('No error detected during the utility check.', 'green'))
        else:
            print(colored(f"{error} errors have been detected during the utility check.", 'red'))
            
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--update", "-u", help="Update the source data of the program", action="store_true")
    parser.add_argument("--hero", help="When in update mode, specify a specific hero to update to avoid updating the whole database")
    parser.add_argument("--check", "-c", help="Perform a validation to check if the customized utility constants in the scripts satisfy the rules."
                        , action="store_true")
    parser.add_argument('--shutdown', '-s', help="When in update mode, shutdown the system when the update finishes", action='store_true')
    args = parser.parse_args()
    
    if args.check:
        if not dota.check_database_integrity():
            sys.exit("Warning: Database information not integrated. Try run the program with '-u' or '--update' option to rebuild the database before performing utility checks.")
        dota.utility_check()
    
    if args.update:
        # Execute update command
        if args.hero:
            
            # Update record of a specific hero
            if hero := dota.authenticate(args.hero):
                bar = ChargingBar(f"Updating {hero} records...", max=122)
                if dota.update_matchup_records(hero, bar):
                    bar.finish()
                    print("Hero matchup data updated successfully!")
                else:
                    bar.finish()
                    print("Failed to update hero matchup data")
                    
        else:
            # Update the whole database
            
            # Ask the user for confirmation if table data exists in the database
            if execute_read_query(dota.cursor, "SELECT name FROM sqlite_master WHERE type='table' AND name='heroes' OR name='hero_counter';"):
                
                if not confirm("Preparing to update the database. This will overwrite the existing data. Proceed? (Y/N) "):
                    sys.exit()
                
                if args.shutdown:
                    if not confirm("The program will shutdown the system when the update finishes. Confirm? (Y/N) "):
                        sys.exit()
                    
                dota.update_data()
                if args.shutdown:
                    shutdown()
            else:
                dota.update_data()
                          

    if not args.check and not args.update:
        # Run the actual program
        
        # Check database integrity
        if not dota.check_database_integrity():
            sys.exit("Warning: Database information not integrated. Try run the program with '-u' or '--update' option to rebuild the database.")
            
        # Ask user to input a role and error checking
        while True:
            if role := input("Input your role (c: carry, m: mid, s: support, o: offlane): "):
                role = role[0].lower()
            else:
                sys.exit("No role inputted")
                
            if role not in ("s", "m", "c", "o"):
                print("Invalid Role")
            else:
                break

        heroes = []
        
        while len(heroes) < 4:
            hero = input("Input a hero or see result (command: 'result'): ").strip()
            if hero.lower() == "result":
                print(generate_result(heroes, role))
            elif match := dota.authenticate(hero):
                try:
                    heroes.index(match)
                except ValueError:
                    heroes.append(match)
                    print("Heroes:", heroes)
                else:
                    print("Hero already exists")
            elif hero.endswith('-a') and (match := dota.authenticate(hero[:-2])):
                print(analyze(match, heroes))
            else:
                print("Unrecognized hero name")
        print("Reached max hero number, printing results: ")
        print(generate_result(heroes, role))
        
        while True:
            final = input("Input final enemy hero: ")
            if match := dota.authenticate(final):
                try:
                    heroes.index(match)
                except ValueError:
                    heroes.append(match)
                    print("Heroes:", heroes)
                    break
                else:
                    print("Hero already exists!")
            elif final.endswith('-a') and (match := dota.authenticate(final[:-2])):
                print(analyze(match, heroes))
            else:
                print("Unrecognized hero name")
        
        while True:
            yours = input("Input your chosen hero: ")
            if yours := dota.authenticate(yours):
                break
            else:
                print("Unrecognized hero name")
                
        print(analyze(yours, heroes))

def generate_result(heroes, role):
    hero_ids = list(map(lambda a: a[0], execute_read_query(dota.cursor, "SELECT id FROM heroes;")))
    
    for hero in heroes:
        hero_ids.remove(dota.name_to_id(hero))
    
    # Hero_scores stores all hero scores countering the given heroes    
    hero_scores = {dota.id_to_name(id): evaluate_against(id, *heroes) for id in hero_ids}
    hero_scores = dict(sorted(hero_scores.items(), key=lambda a: a[1]))
    
    if role == "c":
        result = [["Carry", "Advantage"]]
    elif role == "m":
        result = [["Mid", "Advantage"]]
    elif role == 'o':
        result = [["Offlane", "Advantage"]]
    else:
        result = [["Support", "Advantage"]]

    for hero in hero_scores:
        data_str = f"{hero}{hero_scores[hero]}\n"
        groups = dota.HERO_GROUP.get(hero, "other")
        if role in groups:
            result.append([hero, f"{hero_scores[hero]}%"])
    return tabulate(result)

def evaluate_against(hero_id, *counter):
    '''
        evaluate a hero's advantage rate against a list of atmost 4 counter heroes.
        counter is a sequence that stores counter hero names.
    '''
    score = 0
    for opnt in counter:
        res = execute_read_query(dota.cursor, "SELECT advantage FROM hero_counter WHERE id_hero = ? AND id_counter_hero = ?",
                                    hero_id, dota.name_to_id(opnt))
        try:
            rating = res[0][0]
            score += rating
        except IndexError:
            raise ValueError(f"Hero counter information not found: number {hero_id} hero against {opnt}")
        
    return round(score, 4)

def analyze(yours, heroes):
    analyze = [['Enemy', f'{yours} advantage']]
    total = 0
    for opn in heroes:
        score = evaluate_against(dota.name_to_id(yours), opn)
        total += score
        analyze.append([opn, f'{score}%'])
        
    key = lambda x: float('inf') if analyze.index(x) == 0 else float(x[1][:-1])
    analyze = sorted(analyze, key=key, reverse=True)
    analyze.append(['Overall', f'{total:.5}%'])
    return tabulate(analyze)



if __name__ == "__main__":
    main()