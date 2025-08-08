import random
from google import genai

POS_OUTCOME=1
NEU_OUTCOME=0
NEG_OUTCOME=-1

class Game:
    def __init__(self):
        self.completion_meter=3
        self.win_condition=7
        self.loss_condition=0
        self.current_scene=''
        self.tempo=0
        self.game_context=[]
        self.client = genai.Client()
        self.chat = self.client.chats.create(model="gemini-2.5-flash-lite")
        
    def initialize_game(self):
        # set he inintial scene
        response = self.chat.send_message("You are the narrator for a classic dungeon crawler style text based RPG.  You will guide the player through a series of scenes while they make decisions that lead to their ultimate success or failure.  At times, you will be given secret information about the game state to guide your storytelling.  When you are given secret information, do not include it directly in the story, but let it guide your narrative.  Begin by providing a two to three brief sentences to set the stage for the player, followed by one or two sentences describing the objective at the end of the dungeon.  Remember details like the game objective in case they need to be referenced later.")
        # At times, you will be given secret information about the game state to guide your storytelling.  When you are given secret information, do not include it directly in the story, but let it guide your narrative.
        print(response.text)
        self.game_context.append(response.text)
        return
    
    def play_game(self):
        while self.completion_meter not in [self.win_condition, self.loss_condition]:
            # generate options for the player to choose based on the scene
            options=self.request_options()
            print('1. ', options[0])
            print('2. ', options[1])
            print('\n')
            selection=''
            while selection not in ['1','2']:
                selection=input("Make a selection: ")
            selected_option=options[int(selection)-1]
            
            # act on the choice made by the player
            # currently just random, TODO game logic later
            self.tempo=self.calculate_result() 
            self.completion_meter+=self.tempo
            text_result=self.request_result(self.tempo, selection)
            print(text_result,'\n')

            scene=self.request_scene()
            print(scene,'\n')

            
        if self.completion_meter==self.win_condition:
            print("you win :)")
        else:
            print("you lose :(")
        return
    
    def calculate_result(self):
        # choose a result randomly from [1,0,-1]
        # corresponding to negative, neutral, and positive outcome
        # currently stacked to POS more often in order to better test game progression.
        return random.choice([POS_OUTCOME,POS_OUTCOME,NEU_OUTCOME,NEG_OUTCOME])
    
    def request_scene(self):
        response = self.chat.send_message("The player has a completion score of {}.  A score of {} means that they win the game and achieve the ultimate objective of the story.  A score of {} means that the game is lost.  Now that the player has taken an action and been appropriately punished or rewarded by the fates, it is time to present them with the scene as it currently stands.  Take into account the path that has gotten them to his point, reference the objective if it is appropriate and relevant to the current scene.".format(self.completion_meter, self.win_condition, self.loss_condition))
#        background = ' '.join(self.game_context)
        scene=response.text + ' ({})'.format(self.completion_meter) 
        return scene
    
    def request_options(self):
        options=[]
        response = self.chat.send_message("Given the scene as it currently exists, player needs to be presented with two choices to proceed. In a single sentence, present the first option. This first option should be marginally more cautious or reserved, but stull work to advance the narrative.  Do not explicitly tell the player that this is a safer path.")
        options.append(response.text)
        response = self.chat.send_message("Now, in a single sentence, provide a second option for the player, which might take them down a different path, but will still ultimately lead to their goal.  This option should appear somewhat more risky, with the possibility of greater success; however you should not make this explicit to the player.")
        options.append(response.text)
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

