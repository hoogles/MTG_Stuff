# MTG_Stuff
Just stuff I'm doing for fun to analyze MTG cards.

The main goal is to predict cost based off the contents of the card.

Current issue:
In order to finish the model, I need to integrate the rules text of the card. Skipgrams made the most sense initially, but may be insufficient. Ideally I can create a vector of each action the rule enables but activations enabling something are tough to interpret into a vector. ex, Niv Mizzet giving card draw whenever you cast an instant and sorcery vs a card like Opt that just says "draw a card." 
