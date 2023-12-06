from agents import agent1,agent2
from cooprator import cooprator
from multiprocessing import Process, Queue, Value
import tensorflow as tf
from config import MODEL_PATH
co=cooprator()
agent1=agent1(co)
agent2=agent2(co)
# model1=tf.keras.models.load_model(MODEL_PATH+'/model.h5',{'loss':agent1.FedProx_loss})
# model1.compile(loss=agent1.FedProx_loss,optimizer=tf.keras.optimizers.SGD(0.1),metrics=['mae','mse'])
# model2=tf.keras.models.load_model(MODEL_PATH+'/model.h5',{'loss':agent2.FedProx_loss})
# model2.compile(loss=agent2.FedProx_loss,optimizer=tf.keras.optimizers.SGD(0.1),metrics=['mae','mse'])
# agent1.main_network=model1
# agent2.main_network=model2
# agent1.target_network=model1
# agent2.target_network=model2
for _ in range(50):
    print('>>>>>>>> ',_)
    weights=[agent1.main_network.weights,agent2.main_network.weights]
    co.fedavg_aggregate(weights)
    agent1.last_aggregation_weights=co.last_weights
    agent2.last_aggregation_weights=co.last_weights
    agent1.main_network.set_weights(co.last_weights)
    agent2.main_network.set_weights(co.last_weights)
    agent1.train_local_models()
    agent2.train_local_models()
    co.save_model(agent1.main_network)
    