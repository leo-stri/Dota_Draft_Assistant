from project import dota, generate_result, evaluate_against
from pytest import raises
from helpers import create_connection
from tabulate import tabulate
from termcolor import colored


# Create the mock database and change the cursor pointer
con = create_connection("test_files/test.db")
dota.cursor = con.cursor()

def config_default():
    dota.HERO_ALIAS = {'np': 'natures-prophet', 'b': 'bane', 'i': 'io', 'sl': "slark"}
    dota.HERO_GROUP = {'bane': ('s',), 'natures-prophet': ('c', 'm', 'o'),'io': ('s', 'm', 'o'), 'slark': ('c',)}
    dota.HERO_TOTAL = 4

config_default()

def test_dota_parse_counter_response():
    with open("test_files/counter_response_1.txt") as f:
        content = f.read()
    assert dota.parse_counter_response(content) == {"meepo": -1.29, "lone-druid": -3.7851, "slardar": 0.985}
    
    with open("test_files/counter_response_2.txt") as f:
        content = f.read()
    assert dota.parse_counter_response(content) == {"phantom-lancer": -6.3869, "winter-wyvern": 0, "slark": 10.5639}
    
    with open("test_files/counter_response_3.txt") as f:
        content = f.read()
    with raises(ValueError):
        assert dota.parse_counter_response(content)
    
def test_name_to_id():
    assert dota.name_to_id('bane') == 3
    assert dota.name_to_id('io') == 91
    assert dota.name_to_id('slark') == 93
    assert dota.name_to_id('natures-prophet') == 53
    with raises(ValueError):
        assert dota.name_to_id('unknown')
        
def test_id_to_name():
    assert dota.id_to_name(3) == 'bane'
    assert dota.id_to_name(91) == 'io'
    assert dota.id_to_name(93) == 'slark'
    with raises(ValueError):
        assert dota.id_to_name(150)
        
def test_name_format():
    assert dota.name_format("IDINA") == "idina"
    assert dota.name_format("Mary John") == "mary-john"
    assert dota.name_format("junior's chIor") == "juniors-chior"
    
def test_alias():
    assert dota.alias('b') == 'bane'
    assert dota.alias('np') == 'natures-prophet'
    assert dota.alias('unknown') == 'unknown'
    
def test_authenticate():
    assert dota.authenticate('i') == 'io'
    assert dota.authenticate('invalid') == ''
    assert dota.authenticate("Nature's Prophet") == 'natures-prophet'
    
def test_check_database_integrity():
    assert dota.check_database_integrity() == True
    
    dota.cursor = create_connection('test_files/test_3_hero_record.db').cursor()
    assert dota.check_database_integrity() == False
    
    dota.cursor = create_connection('test_files/test_false_structure.db').cursor()
    assert dota.check_database_integrity() == False
    
    dota.cursor = create_connection('test_files/test_missing_counter_record.db').cursor()
    assert dota.check_database_integrity() == False
    
    dota.cursor = create_connection('test_files/test_missing_index.db').cursor()
    assert dota.check_database_integrity() == False
    
    dota.cursor = con.cursor()
    
def test_utility_check(capsys):
    dota.HERO_GROUP = {'bane': ('s',), 'io': ('s', 'm', 'o'), 'slark': ('c',), 'natures-prophet': ('c', 'm', 'o'), 'none': ('m',), 'invalid': ('o', 'm')}
    dota.utility_check()
    assert capsys.readouterr().out == 'HERO_GROUP validation report: 2 excessive heroes listed\nHERO_GROUP validation report: name none in HERO_GROUP is not a valid hero name\nHERO_GROUP validation report: name invalid in HERO_GROUP is not a valid hero name\n'\
            + colored("3 errors have been detected during the utility check.", 'red') + "\n"
    
    dota.HERO_GROUP = {'bane': ('s',), 'natures-prophet': ('c', 'm', 'o')}
    dota.utility_check()
    assert capsys.readouterr().out == 'HERO_GROUP validation report: io is missing from the list\nHERO_GROUP validation report: slark is missing from the list\n'\
            + colored("2 errors have been detected during the utility check.", 'red') + "\n"
            
    dota.HERO_GROUP = {'bane': 's', 'io': ('s', 'm', 'o'), 'slark': ('c',), 'natures-prophet': ('c', 'l', 'o')}
    dota.utility_check()
    assert capsys.readouterr().out == 'HERO_GROUP validation report: value of hero bane s is not a valid data type: must be a tuple\nHERO_GROUP Validation report: unrecognized role indicator in the group definition of hero natures-prophet: l\n'\
            + colored("2 errors have been detected during the utility check.", 'red') + "\n"
    
    config_default()
    dota.HERO_ALIAS = {'np': 'natures-prophet', 'b': 'bane', 'i': 'io', 'sl': "slar"}
    dota.utility_check()
    assert capsys.readouterr().out == 'HERO_ALIAS Validation report: alias sl points to an unrecognized hero name: slar\n'\
            + colored("1 errors have been detected during the utility check.", 'red') + "\n"
            
    config_default()
    dota.utility_check()
    assert capsys.readouterr().out == colored("No error detected during the utility check.", 'green') + "\n"
    
def test_generate_result():
    assert generate_result(['io', 'natures-prophet'], 's') == tabulate([['Support', 'Advantage'], ['bane', "8.0%"]])
    assert generate_result(['bane', 'io'], 'c') == tabulate([['Carry', 'Advantage'], ['natures-prophet', "-1.0%"],['slark', '4.0%']])
    assert generate_result(['slark'], 'o') == tabulate([['Offlane', 'Advantage'], ['natures-prophet', '1.0%'], ['io', '5.0%']])
    
def test_evaluate_against():
    assert evaluate_against(91, 'bane', 'natures-prophet') == -5
    assert evaluate_against(3, 'io') == 3
    assert evaluate_against(53, 'io', 'slark', 'bane') == 0
    
    with raises(ValueError):
        assert evaluate_against(53, 'invalid')
        
    with raises(ValueError):
        assert evaluate_against(150, 'bane')