import spacy
from rasa.nlu.training_data  import load_data
from rasa.nlu.config import RasaNLUModelConfig
from rasa.nlu.model import Trainer, Interpreter
from rasa.nlu import config

def train(file: str = ""):
    train_data = load_data("training/" + file)
    trainer = Trainer(config.load("config.yml"))
    trainer.train(train_data)
