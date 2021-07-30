"""
The main script to run the training or evaluation
"""

from absl import app, logging
from pysc2.env.sc2_env import SC2Env, AgentInterfaceFormat, Dimensions, Agent, Race
from pysc2.lib import actions

# ! hyper-parameters
# * for the environment
MAP_NAME = "CollectMineralsAndGas"
MAP_SIZE = 64
STEP_INTERVAL = 16
VISUALIZE_FEATURE_MAPS = False
logging.set_verbosity(logging.ERROR)
ACTION_SPACE = len(actions.FUNCTIONS)

# * for the training
# ** common
GAMMA = 0.99
ACTOR_LEARNING_RATE = 0.0003
CRITIC_LEARNING_RATE = 0.001
RANDOM_SEED = 1234
# ** DDPG
REPLAY_BUFFER_SIZE = 10000
TAU = 0.005
BATCH_SIZE = 32
WARM_STEPS = 1000
UPDATE_STEPS = 1000
# ** PPO
CLIP_RATIO = 0.2
ACTOR_TRAINING_ITERATIONS = 80
CRITIC_TRAINING_ITERATIONS = 80
LAMBDA = 0.97
TARGET_KL = 10
MAX_TRAJECTORY_LENGTH = 1000

# * for model training and saving
SAVE_PATH = "./Saves/"
MODEL_NAME = "CMAG_V1_RE"
SAVE_EPOCHS = 500
EPOCHS = 10000

# * for restoring training
RESTORE = False
TOKEN = "5000"
RESTORE_TOKEN = 1

# ! choosing one algorithm: now supports DDPG, PPO
ALGORITHM = "DDPG"


def main(args):
    # instantiate the environment
    agent_interface_format = AgentInterfaceFormat(feature_dimensions=Dimensions(screen=MAP_SIZE,
                                                                                minimap=MAP_SIZE))

    env = SC2Env(map_name=MAP_NAME,
                 players=[Agent(Race.terran)],
                 agent_interface_format=agent_interface_format,
                 step_mul=STEP_INTERVAL,
                 visualize=VISUALIZE_FEATURE_MAPS)

    # instantiate the agent/algorithm
    if ALGORITHM == "DDPG" or "ddpg":
        from Algorithms.DDPG import DDPG
        from Networks.Actors import DDPGActorNet
        from Networks.Critics import DDPGCriticNet

        agent = DDPG(env=env,
                     actor=DDPGActorNet(),
                     critic=DDPGCriticNet(),
                     replay_buffer_size=REPLAY_BUFFER_SIZE,
                     actor_lr=ACTOR_LEARNING_RATE,
                     critic_lr=CRITIC_LEARNING_RATE,
                     gamma=GAMMA,
                     tau=TAU,
                     batch_size=BATCH_SIZE,
                     warmup_steps=WARM_STEPS,
                     update_steps=UPDATE_STEPS,
                     map_size=MAP_SIZE,
                     seed=RANDOM_SEED,
                     action_space=ACTION_SPACE,
                     save_path=SAVE_PATH,
                     model_name=MODEL_NAME,
                     save_epochs=SAVE_EPOCHS)

    elif ALGORITHM == "PPO" or "ppo":
        from Algorithms.PPO import PPO
        from Networks.Actors import PPOActorNet
        from Networks.Critics import PPOCriticNet

        agent = PPO(env=env,
                    actor=PPOActorNet(),
                    critic=PPOCriticNet(),
                    gamma=GAMMA,
                    clip_ratio=CLIP_RATIO,
                    actor_lr=ACTOR_LEARNING_RATE,
                    critic_lr=CRITIC_LEARNING_RATE,
                    actor_train_iterations=ACTOR_TRAINING_ITERATIONS,
                    critic_train_iterations=CRITIC_TRAINING_ITERATIONS,
                    lamb=LAMBDA,
                    max_trajectory_length=MAX_TRAJECTORY_LENGTH,
                    target_kl=TARGET_KL,
                    seed=RANDOM_SEED,
                    action_space=ACTION_SPACE,
                    map_size=MAP_SIZE,
                    save_path=SAVE_PATH,
                    model_name=MODEL_NAME,
                    save_epochs=SAVE_EPOCHS)

    else:
        print("The algorithm {} is not supported for now.".format(ALGORITHM))
        return

    if RESTORE:
        agent.restore(TOKEN, EPOCHS, RESTORE_TOKEN)
    else:
        agent.learn(EPOCHS)


if __name__ == "__main__":
    app.run(main)
