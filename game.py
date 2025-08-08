import random
from google import genai
from google.genai import types

POS_OUTCOME=1
NEU_OUTCOME=0
NEG_OUTCOME=-1

CAUTIOUS=10
CAUTIOUS_CHOICE=[NEU_OUTCOME,POS_OUTCOME]
RISKY=11
RISKY_CHOICE=[POS_OUTCOME,NEG_OUTCOME]
WILD=12
WILD_CHOICE=[NEG_OUTCOME,NEU_OUTCOME,POS_OUTCOME]
UNWISE=13
UNWISE_CHOICE=[NEU_OUTCOME,NEG_OUTCOME]

class Game:
    def __init__(self):
        self.current_scene=''
        self.tempo=0
        self.game_context=[]
        self.completion_meter=3
        self.win_condition=7
        self.loss_condition=0
        with open('system_prompt.txt', 'r') as f:
            self._config_text=f.read().format(self.win_condition, self.loss_condition, self.win_condition)
        self.config=types.GenerateContentConfig(system_instruction=self._config_text)
        self.client = genai.Client()
        self.chat = self.client.chats.create(model="gemini-2.5-flash-lite",config=self.config)
        
    def initialize_game(self):
        # set he inintial scene
        bg_prompt="""In the format of a list, briefly describe the setting of the game by answering the following questions.  Be specific in your answers, providing examples wherever possible, so that you can use these details to guide the story later on.  This list will not be given directly to the player, but will provide the framework for the story they explore.  Remember these details to maintain continuity throughout the story.

        What is the name of the place our player finds themself in?
        What is the player's goal in this place?
        Is the place inhabited?
        What types of trials stand between the player and their goal?
        """

        background_info=self.chat.send_message(bg_prompt)
        response = self.chat.send_message("Begin by providing two to three brief sentences to set the stage for the player, followed by one or two sentences describing the objective at the end of the dungeon, separated by a paragraph break.")
        print(response.text + '\n')
        self.game_context.append(response.text)
        return
    
    def play_game(self):
        while self.completion_meter not in [self.win_condition, self.loss_condition]:
            # generate options for the player to choose based on the scene
            options=self.request_options()
            print('1: ', options[0]['response'])
            print('2: ', options[1]['response'])
            print('\n')
            selection=''
            while selection not in ['1','2']:
                selection=input("Make a selection: ")
            print('\n')
            selected_option=options[int(selection)-1]
            
            # act on the choice made by the player
            self.tempo=self.calculate_result(selected_option['dist']) 
            self.completion_meter+=self.tempo
            text_result=self.request_result(self.tempo, selected_option['response'])
            print(text_result,'\n')

            scene=self.request_scene()
            print(scene,'\n')
            
        if self.completion_meter==self.win_condition:
            print("you win :)")
        else:
            print("you lose :(")
        return
    
    def calculate_result(self,outcomes):
        if not outcomes:
        # choose a result randomly from [1,0,-1]
        # corresponding to negative, neutral, and positive outcome
            return random.choice([POS_OUTCOME,NEU_OUTCOME,NEG_OUTCOME])
        # otherwise choose randomly from the distribution provided
        return random.choice(outcomes)
    
    def request_scene(self):
        prompt_request_scene="The player has a completion score of {}. Now that the player has taken an action and been appropriately punished or rewarded by the fates, it is time to present them with the scene as it currently stands.  Take into account the path that has gotten them to his point, reference the objective if it is appropriate and relevant to the current scene.".format(self.completion_meter)
        response = self.chat.send_message(prompt_request_scene)
        # completion score included in printout for debug purposes
        scene=response.text + ' ({})'.format(self.completion_meter) 
        return scene
    
    def request_options(self):
        options=[]
        prompt_cautious='should be somewhat cautious or reserved, but still work to advance the narrative'
        prompt_risky='should appear somewhat risky, with the possibility of greater success'
        prompt_wildcard='should provide the player a chance to act in an unexpected way, possibly leading to a unique outcome'
        prompt_unwise='should be a reckless and inadvisable action, likely to endanger the player'
        possible_options=[(CAUTIOUS_CHOICE,prompt_cautious,CAUTIOUS),
                          (RISKY_CHOICE,prompt_risky,RISKY),
                          (WILD_CHOICE,prompt_wildcard,WILD),
                          (UNWISE_CHOICE,prompt_unwise,UNWISE)]
        # randomly choose two of the four options.  sometimes the player will be given safe options, sometimes risky or unwise options
        choices=random.sample(possible_options,2)
        response = self.chat.send_message("Given the scene as it currently exists, player needs to be presented with two alternative ways to proceed.  Each option should be presented in as a single sentence describing a possible action that the player could take.  Separate these choices by a paragraph break. The first option {}. The second option {}.  Do not explicitly tell the player whether an option is safe or risky.".format(choices[0][1],choices[1][1]))

        # options is a list of dicts, each containing a response and outcome distribution 
        options=[]
        for i,r in enumerate(response.text.split('\n\n')):
            options.append({'dist':choices[i][0],'response':r + ' ({})'.format(choices[i][2])})
        return options
    
    def request_result(self,num_result,option):
        message='The player selected the following option: "{}". '.format(option)
        if num_result == POS_OUTCOME:
            message += 'The player was successful this round.  They are advancing toward their ultimate goal. '
        elif num_result == NEU_OUTCOME:
            message += 'The player did not make progress this round.  While they did not advance toward their ultimate goal, neither did they suffer any harm. '
        elif num_result == NEG_OUTCOME:
            message += 'The player was unsuccessful this round.  They did not make progress toward their ultimate goal, and have suffered some sort of setback or harm; although the goal is still achievable, it is now further away. '
        message += 'In one or two brief sentences, describe what the player experiences as they perform the action they chose.'
        response = self.chat.send_message(message)
        return response.text

    def render(self,text):
        print(text)
    
def main():
    random.seed()
    g = Game()
    g.initialize_game()
    g.play_game()
    return

if __name__=="__main__":
    main()

    # part 1: silly little dungeon crawler 
#
# basic game loop
#  - determine objective by prompting LLM
#  - while game is not won or lost:
#    - present player with (n) options:
#    - player makes decision.
#      - outcome of decision determined using dice roll
#      - outcome moves the needle on the win/loss meter
#    - if game is won/lost
#      end game

# each step should go: [scene, options->decision, result]

