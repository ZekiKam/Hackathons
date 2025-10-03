import sys, os
import numpy as np
import json
from datetime import datetime
from cache.Cache import Cache
from agents.CacheAgent import *
from agents.DQNAgent import DQNAgent
from agents.ReflexAgent import *
from cache.DataLoader import DataLoaderPintos
from optimize_dqn import DQNCacheOptimizer

def run_optimization(file_paths, cache_size=50):
    """
    Run hyperparameter optimization using Optuna.
    
    Args:
        file_paths: List of dataset file paths
        cache_size: Size of the cache
    """
    print("\n" + "="*80)
    print("STARTING HYPERPARAMETER OPTIMIZATION")
    print("="*80 + "\n")
    
    # Create optimizer
    optimizer = DQNCacheOptimizer(
        file_paths=file_paths,
        cache_size=cache_size,
        n_trials=50,
        n_episodes=20,
        timeout=None,
        study_name="dqn_cache_optimization",
        storage=None,
        feature_selection=('Base',),
        reward_params=dict(name='our', alpha=0.5, psi=10, mu=1, beta=0.3)
    )
    
    # Run optimization
    study = optimizer.optimize(load_if_exists=True)
    
    # Print results
    optimizer.print_study_results(study)
    
    # Save best parameters
    optimizer.save_best_params(study, "best_dqn_params.json")
    
    # Plot optimization history (requires plotly)
    try:
        optimizer.plot_optimization_history(study, save_path="optimization_results")
    except:
        print("\nSkipping plots (install plotly for visualization)")
    
    return study


def run_evaluation(file_paths, cache_size=50, use_optimized=False, params_file="best_dqn_params.json"):
    """
    Evaluate agents on test datasets.
    
    Args:
        file_paths: List of dataset file paths
        cache_size: Size of the cache
        use_optimized: Whether to use optimized hyperparameters
        params_file: Path to optimized parameters file
    """
    print("\n" + "="*80)
    print("EVALUATING AGENTS")
    print("="*80 + "\n")
    
    # Store results for JSON export (simplified structure)
    results_json = []
    
    for path in file_paths:
        case_name = os.path.basename(path)
        print("==================== Testcase %s ====================" % case_name)

        # cache
        dataloader = DataLoaderPintos(path)
        env = Cache(dataloader, cache_size
            , feature_selection=('Base',)
            , reward_params = dict(name='our', alpha=0.5, psi=10, mu=1, beta=0.3)
            , allow_skip=False
        )
        
        # agents
        agents = {}
        
        # Create DQN agent with optimized or default parameters
        if use_optimized and os.path.exists(params_file):
            print(f"Using optimized parameters from {params_file}")
            agents['DQN'] = DQNCacheOptimizer.create_optimized_agent(params_file, env)
        else:
            print("Using default parameters")
            agents['DQN'] = DQNAgent(env.n_actions, env.n_features,
                learning_rate=0.01,
                reward_decay=0.9,

                # Epsilon greedy
                e_greedy_min=(0.0, 0.1),
                e_greedy_max=(0.2, 0.8),
                e_greedy_init=(0.1, 0.5),
                e_greedy_increment=(0.005, 0.01),
                e_greedy_decrement=(0.005, 0.001),

                history_size=50,
                dynamic_e_greedy_iter=25,
                reward_threshold=3,
                explore_mentor = 'LRU',

                replace_target_iter=100,
                memory_size=10000,
                batch_size=128,

                output_graph=False,
                verbose=0
            )
        
        # Baseline agents
        agents['Random'] = RandomAgent(env.n_actions)
        agents['LRU'] = LRUAgent(env.n_actions)
        agents['LFU'] = LFUAgent(env.n_actions)
        agents['MRU'] = MRUAgent(env.n_actions)
    
        for (name, agent) in agents.items():
            print("-------------------- %s --------------------" % name)
            step = 0
            miss_rates = []    # record miss rate for every episode
            
            # determine how many episodes to proceed
            # 100 for learning agents, 20 for random agents
            # 1 for other agents because their miss rates are invariant
            if isinstance(agent, LearnerAgent):
                episodes = 100
            elif isinstance(agent, RandomAgent):
                episodes = 20
            else:
                episodes = 1

            for episode in range(episodes):
                # initial observation
                observation = env.reset()

                while True:
                    # agent choose action based on observation
                    action = agent.choose_action(observation)

                    # agent take action and get next observation and reward
                    observation_, reward = env.step(action)

                    # break while loop when end of this episode
                    if env.hasDone():
                        break

                    agent.store_transition(observation, action, reward, observation_)

                    if isinstance(agent, LearnerAgent) and (step > 20) and (step % 5 == 0):
                        agent.learn()

                    # swap observation
                    observation = observation_

                    if step % 100 == 0:
                        mr = env.miss_rate()

                    step += 1

                # report after every episode
                mr = env.miss_rate()
                print("Agent=%s, Case=%s, Episode=%d: Accesses=%d, Misses=%d, MissRate=%f"
                    % (name, case_name, episode, env.total_count, env.miss_count, mr)
                )
                miss_rates.append(mr)

            # summary
            miss_rates = np.array(miss_rates)
            mean_mr = float(np.mean(miss_rates))
            
            print("Agent=%s, Case=%s: Mean=%f, Median=%f, Max=%f, Min=%f"
                % (name, case_name, mean_mr, np.median(miss_rates), np.max(miss_rates), np.min(miss_rates))
            )
            
            # Store simplified result for JSON (multiply by 100 to get percentage)
            results_json.append({
                "algorithm": name,
                "miss_rate": round(mean_mr * 100, 2)
            })
            
            # Clean up DQN agent
            if name == 'DQN':
                agent.sess.close()
    
    # Save simplified JSON
    json_output_path = "results.json"
    with open(json_output_path, 'w') as f:
        json.dump(results_json, f, indent=2)
    
    print("\n" + "="*80)
    print(f"RESULTS SAVED TO: {json_output_path}")
    print("="*80)
    print("JSON Contents:")
    json.dumps(results_json, indent=2)
    print("\n" + "="*80)


if __name__ == "__main__":
    # disk activities
    file_paths = [
        "blocksector_format.csv"
    ]
    
    # Check if best parameters already exist
    params_file = "best_dqn_params.json"
    
    if os.path.exists(params_file):
        print("\n" + "="*80)
        print(f"FOUND EXISTING PARAMETERS: {params_file}")
        print("="*80)
        print("Skipping optimization and running evaluation with existing parameters...\n")
        
        # Run evaluation only
        run_evaluation(
            file_paths, 
            cache_size=50, 
            use_optimized=True,
            params_file=params_file
        )
    else:
        print("\n" + "="*80)
        print(f"NO EXISTING PARAMETERS FOUND: {params_file}")
        print("="*80)
        print("Starting hyperparameter optimization...\n")
        
        # Run optimization first
        study = run_optimization(file_paths, cache_size=50)
        
        # Then run evaluation with optimized parameters
        print("\n" + "="*80)
        print("RUNNING EVALUATION WITH OPTIMIZED PARAMETERS")
        print("="*80 + "\n")
        
        run_evaluation(
            file_paths, 
            cache_size=50, 
            use_optimized=True,
            params_file=params_file
        )