from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer,MetaData,Interpreter
from rasa_nlu import config
import rasa_nlu.convert

def train(dataset:str):

    train_data = load_data(dataset)
    trainer = Trainer(config.load("training/config.yml"))
    trainer.train(train_data)

train("training/tasks_data.json")

from rasa_nlu.training_data import load_data
from rasa_nlu.config import RasaNLUModelConfig
from rasa_nlu.model import Trainer, Metadata, Interpreter
from rasa_nlu import config
dataset="training/tasks_data.json"
train_data = load_data(dataset)
trainer = Trainer(config.load("training/config.yml"))
trainer.train(train_data)
model_directory = trainer.persist('models/')
interpreter = Interpreter.load(model_directory)
interpreter.parse("Add task help Melissa to prepare for work issues")