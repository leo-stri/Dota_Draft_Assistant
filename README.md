# DRAFT ASSISTANT
## Description:
This project is a program designed for dota2 in-game play specifically. I personally think dota as a really drafting-centric game, so the hero you pick depending on the enemy draft will have a great influence on your win rate of this game. Before I came up with this program, I have been browsing the website DotaBuff.com very often just to see the what heroes are good for countering the enemy draft, for on DotaBuff there is very complete information about which hero counters which hero and their advantage rate accordingly.

Draft Assistant is a program that automates the process of browsing DotaBuff for you. It fetches data from DotaBuff and stores it in the local database, and it does automated queries everytime you tell it what enemy heroes have been picked and generates the best picks for you.

## Project Files
folder: test_files contains some mock database and sample html files for testing purpose

dota.db: the central database that contains all information about heroes and hero counters

helpers.py: a python file that contains some self-defined helper function.

project.py: contains main codings.

test_project.py: A python test file that uses pytest.

## Usage:
For first-time users: run 'python project.py -u' or 'python project.py --update' to build the database. During this the program will fetch data from OpenDota.com and DotaBuff.com, it would take a while and requires stable internet connection. After building the database, you can still run the program with '-u' command to update your data to the newest.

If certain heroes failed to load in during the data update, use the command 'python project.py -u -h {hero name}' to update information for a certain hero to complete the database.

To run the program use command 'python project.py' without any command-line arguments. The program will prompt you for an input of your role (between 'c' as in 'carry', 'm' as in 'mid', 'o' as in 'offlane', 's' as in 'support'), then you need to start inputting enemy heroes that have been picked while you are playing the game (Be sure to not be too hasty to pick your hero too). You can type in 'result' anytime to ask the program to generate the current best picks for you according to the enemy heroes that you have inputted so far. The program will show all the possible picks and arrange them from worst to best according to their advantage rates that the program has calculated.

While you're inputting enemy heroes, you can also type in input such as '{hero name} -a' that has a '-a' suffix after a valid hero name, to query the program for how well a certain hero is doing so far in this game. The program will do an analyze of the inputted hero with '-a' suffix that includes the advantage rate of this hero against each enemy hero and the overall advantage of this hero.

After you reach 4 maximum inputted enemy heroes (which is the maximum number of enemy heroes that will be picked before you definitely have to pick your hero, while the 5th enemy hero remains unseen, in a regular dota gameplay currently), the program will automatically generate a result for you that is similar to the one when you type in 'result' keyword. After you finally pick your hero and the enemy team also picks their final hero, the program will prompt you for the enemy final hero and your final choice, according to which you will receive an analyze of how well your hero is doing in this game overall draft-wise.

## Custom configurations:
In the dota class in project.py, there are 3 global variables for your custom configuration.

HERO_GROUP: a dictionary variable that defines what hero belongs to which roles, only according to which will the program decide what heroes to present when you input a certain role. It has been pre-defined but is open to custom configuration. You can add additional roles to some hero you're more comfortable with or remove some roles from the heroes that you're less comfortable with.

HERO_ALIAS: a dictionary variable that defines aliases for all heroes, so you don't have to type the full hero name when you are using the program. It contains a share of pre-defines aliases but you can modify some according to your likes or even add your own aliases.

HERO_TOTAL: a integer global variable that's used as a standard for how many heroes there exists in total. The program will use this variable to check if the database is integrated or not. Change this variable only when the total hero number changes in the game.

Custom variables validation: It is recommended to run the program with '-c' or '--check' option (python project.py -c)everytime you alter the global variables within dota class for custom configuration, to perform a validation check for all the custom variables, in case you mess up with the custom variables and break the program. The program will tell you if there is any error with these variables.
