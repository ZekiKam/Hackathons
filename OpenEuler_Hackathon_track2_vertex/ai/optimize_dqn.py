"""
Optuna Hyperparameter Optimization for DQN Cache Agent

This module provides hyperparameter optimization using Optuna for the DQN agent
used in cache replacement policies.

Usage:
    python optimize_dqn.py
"""

import sys
import os
import numpy as np
import optuna
from optuna.pruners import MedianPruner
from optuna.samplers import TPESampler
import json
from typing import Dict, Any, Optional, List
import warnings
warnings.filterwarnings('ignore')

from cache.Cache import Cache
from agents.DQNAgent import DQNAgent
from agents.ReflexAgent import RandomAgent, LRUAgent, LFUAgent, MRUAgent
from cache.DataLoader import DataLoaderPintos


class DQNCacheOptimizer:
    """
    Optuna-based hyperparameter optimizer for DQN Cache Agent.
    """
    
    def __init__(
        self,
        file_paths: List[str],
        cache_size: int = 50,
        n_trials: int = 50,
        n_episodes: int = 20,
        timeout: Optional[int] = None,
        study_name: str = "dqn_cache_optimization",
        storage: Optional[str] = None,
        feature_selection: tuple = ('Base',),
        reward_params: dict = None
    ):
        """
        Initialize the optimizer.
        
        Args:
            file_paths: List of dataset file paths to use for training
            cache_size: Size of the cache
            n_trials: Number of optimization trials
            n_episodes: Number of episodes to run per trial
            timeout: Time limit for optimization in seconds
            study_name: Name of the Optuna study
            storage: Database URL for distributed optimization
            feature_selection: Feature selection for cache environment
            reward_params: Reward parameters for cache environment
        """
        self.file_paths = file_paths
        self.cache_size = cache_size
        self.n_trials = n_trials
        self.n_episodes = n_episodes
        self.timeout = timeout
        self.study_name = study_name
        self.storage = storage
        self.feature_selection = feature_selection
        
        if reward_params is None:
            self.reward_params = dict(
                name='our',
                alpha=0.5,
                psi=10,
                mu=1,
                beta=0.3
            )
        else:
            self.reward_params = reward_params
        
        # Configure logging
        optuna.logging.set_verbosity(optuna.logging.WARNING)
    
    def objective(self, trial: optuna.Trial) -> float:
        """
        Objective function for Optuna optimization.
        Minimizes the average miss rate across all datasets.
        
        Args:
            trial: Optuna trial object
            
        Returns:
            Average miss rate across all datasets (lower is better)
        """
        # Sample hyperparameters
        params = self._sample_hyperparameters(trial)
        
        all_miss_rates = []
        
        # Test on each dataset
        for path in self.file_paths:
            try:
                # Create environment
                dataloader = DataLoaderPintos(path)
                env = Cache(
                    dataloader,
                    self.cache_size,
                    feature_selection=self.feature_selection,
                    reward_params=self.reward_params,
                    allow_skip=False
                )
                
                # Create DQN agent with sampled parameters
                agent = DQNAgent(
                    env.n_actions,
                    env.n_features,
                    learning_rate=params['learning_rate'],
                    reward_decay=params['reward_decay'],
                    e_greedy_min=(params['e_greedy_min'], params['e_greedy_min']),
                    e_greedy_max=(params['e_greedy_max'], params['e_greedy_max']),
                    e_greedy_init=(params['e_greedy_init'], params['e_greedy_init']),
                    e_greedy_increment=(params['e_greedy_increment'], params['e_greedy_increment']),
                    e_greedy_decrement=(params['e_greedy_decrement'], params['e_greedy_decrement']),
                    reward_threshold=params['reward_threshold'],
                    history_size=params['history_size'],
                    dynamic_e_greedy_iter=params['dynamic_e_greedy_iter'],
                    explore_mentor=params['explore_mentor'],
                    replace_target_iter=params['replace_target_iter'],
                    memory_size=params['memory_size'],
                    batch_size=params['batch_size'],
                    output_graph=False,
                    verbose=0
                )
                
                # Training loop
                miss_rates = []
                step = 0
                
                for episode in range(self.n_episodes):
                    observation = env.reset()
                    
                    while True:
                        # Agent choose action
                        action = agent.choose_action(observation)
                        
                        # Take action
                        observation_, reward = env.step(action)
                        
                        # Check if done
                        if env.hasDone():
                            break
                        
                        # Store transition
                        agent.store_transition(observation, action, reward, observation_)
                        
                        # Learn
                        if step > params['batch_size'] and step % 5 == 0:
                            agent.learn()
                        
                        observation = observation_
                        step += 1
                    
                    # Record miss rate
                    mr = env.miss_rate()
                    miss_rates.append(mr)
                
                # Use the best (minimum) miss rate from all episodes
                dataset_miss_rate = np.min(miss_rates)
                all_miss_rates.append(dataset_miss_rate)
                
                # Clean up TensorFlow session
                agent.sess.close()
                
            except Exception as e:
                print(f"Error processing {path}: {e}")
                # Return a penalty value
                return 1.0
        
        # Average miss rate across all datasets
        avg_miss_rate = np.mean(all_miss_rates)
        
        # Report intermediate value for pruning
        trial.report(avg_miss_rate, len(all_miss_rates))
        
        # Prune unpromising trials
        if trial.should_prune():
            raise optuna.TrialPruned()
        
        return avg_miss_rate
    
    def _sample_hyperparameters(self, trial: optuna.Trial) -> Dict[str, Any]:
        """
        Sample hyperparameters for the trial.
        
        Args:
            trial: Optuna trial object
            
        Returns:
            Dictionary of sampled hyperparameters
        """
        params = {
            # Learning parameters
            'learning_rate': trial.suggest_float('learning_rate', 1e-4, 1e-1, log=True),
            'reward_decay': trial.suggest_float('reward_decay', 0.85, 0.99),
            
            # Epsilon-greedy parameters
            'e_greedy_min': trial.suggest_float('e_greedy_min', 0.0, 0.15),
            'e_greedy_max': trial.suggest_float('e_greedy_max', 0.15, 0.9),
            'e_greedy_init': trial.suggest_float('e_greedy_init', 0.05, 0.6),
            'e_greedy_increment': trial.suggest_float('e_greedy_increment', 0.001, 0.02),
            'e_greedy_decrement': trial.suggest_float('e_greedy_decrement', 0.001, 0.01),
            
            # Dynamic epsilon-greedy parameters
            'reward_threshold': trial.suggest_float('reward_threshold', 0.5, 10.0),
            'history_size': trial.suggest_int('history_size', 20, 100),
            'dynamic_e_greedy_iter': trial.suggest_int('dynamic_e_greedy_iter', 10, 50),
            
            # Exploration mentor
            'explore_mentor': trial.suggest_categorical('explore_mentor', ['LRU', 'LFU']),
            
            # DQN architecture parameters
            'replace_target_iter': trial.suggest_int('replace_target_iter', 50, 300),
            'memory_size': trial.suggest_int('memory_size', 1000, 20000, step=1000),
            'batch_size': trial.suggest_categorical('batch_size', [32, 64, 128, 256]),
        }
        
        return params
    
    def optimize(self, load_if_exists: bool = True) -> optuna.Study:
        """
        Run the optimization.
        
        Args:
            load_if_exists: Whether to load existing study if available
            
        Returns:
            Optuna study object with results
        """
        # Create study (minimize miss rate)
        study = optuna.create_study(
            study_name=self.study_name,
            storage=self.storage,
            direction="minimize",  # Minimize miss rate
            sampler=TPESampler(seed=42),
            pruner=MedianPruner(
                n_startup_trials=5,
                n_warmup_steps=2,
                interval_steps=1
            ),
            load_if_exists=load_if_exists
        )
        
        print(f"Starting optimization with {self.n_trials} trials...")
        print(f"Testing on {len(self.file_paths)} datasets")
        print(f"Episodes per trial: {self.n_episodes}")
        print("-" * 80)
        
        # Run optimization
        study.optimize(
            self.objective,
            n_trials=self.n_trials,
            timeout=self.timeout,
            show_progress_bar=True,
            catch=(Exception,)
        )
        
        return study
    
    @staticmethod
    def print_study_results(study: optuna.Study):
        """
        Print optimization results.
        
        Args:
            study: Completed Optuna study
        """
        print("\n" + "="*80)
        print("OPTIMIZATION RESULTS")
        print("="*80)
        
        print(f"\nNumber of finished trials: {len(study.trials)}")
        
        # Best trial
        print("\nBest trial:")
        trial = study.best_trial
        print(f"  Miss Rate: {trial.value:.6f}")
        print(f"  Trial number: {trial.number}")
        
        print("\n  Best Hyperparameters:")
        for key, value in sorted(trial.params.items()):
            print(f"    {key:25s}: {value}")
        
        # Statistics
        pruned_trials = study.get_trials(deepcopy=False, states=[optuna.trial.TrialState.PRUNED])
        complete_trials = study.get_trials(deepcopy=False, states=[optuna.trial.TrialState.COMPLETE])
        
        print(f"\n  Pruned trials: {len(pruned_trials)}")
        print(f"  Complete trials: {len(complete_trials)}")
        
        # Top 5 trials
        if len(complete_trials) >= 5:
            print("\nTop 5 trials:")
            sorted_trials = sorted(complete_trials, key=lambda t: t.value)[:5]
            for i, t in enumerate(sorted_trials, 1):
                print(f"  {i}. Trial #{t.number}: Miss Rate = {t.value:.6f}")
    
    @staticmethod
    def plot_optimization_history(study: optuna.Study, save_path: Optional[str] = None):
        """
        Plot optimization history and parameter importances.
        
        Args:
            study: Completed Optuna study
            save_path: Path to save the plots (optional)
        """
        try:
            import plotly.graph_objects as go
            from optuna.visualization import (
                plot_optimization_history,
                plot_param_importances,
                plot_parallel_coordinate,
                plot_slice
            )
            
            # Optimization history
            print("\nGenerating optimization history plot...")
            fig1 = plot_optimization_history(study)
            if save_path:
                fig1.write_html(f"{save_path}_history.html")
                print(f"Saved to {save_path}_history.html")
            fig1.show()
            
            # Parameter importances
            print("Generating parameter importance plot...")
            fig2 = plot_param_importances(study)
            if save_path:
                fig2.write_html(f"{save_path}_importances.html")
                print(f"Saved to {save_path}_importances.html")
            fig2.show()
            
            # Parallel coordinate plot
            print("Generating parallel coordinate plot...")
            fig3 = plot_parallel_coordinate(study)
            if save_path:
                fig3.write_html(f"{save_path}_parallel.html")
                print(f"Saved to {save_path}_parallel.html")
            fig3.show()
            
        except ImportError:
            print("\nInstall plotly for visualization: pip install plotly")
        except Exception as e:
            print(f"\nError generating plots: {e}")
    
    @staticmethod
    def save_best_params(study: optuna.Study, filepath: str):
        """
        Save best parameters to a JSON file.
        
        Args:
            study: Completed Optuna study
            filepath: Path to save parameters
        """
        best_params = study.best_trial.params.copy()
        best_params['best_miss_rate'] = study.best_trial.value
        best_params['trial_number'] = study.best_trial.number
        
        with open(filepath, 'w') as f:
            json.dump(best_params, f, indent=4)
        
        print(f"\nBest parameters saved to {filepath}")
    
    @staticmethod
    def create_optimized_agent(params_file: str, env) -> DQNAgent:
        """
        Create a DQN agent with optimized parameters from file.
        
        Args:
            params_file: Path to JSON file with optimized parameters
            env: Cache environment
            
        Returns:
            DQNAgent with optimized parameters
        """
        with open(params_file, 'r') as f:
            params = json.load(f)
        
        agent = DQNAgent(
            env.n_actions,
            env.n_features,
            learning_rate=params['learning_rate'],
            reward_decay=params['reward_decay'],
            e_greedy_min=(params['e_greedy_min'], params['e_greedy_min']),
            e_greedy_max=(params['e_greedy_max'], params['e_greedy_max']),
            e_greedy_init=(params['e_greedy_init'], params['e_greedy_init']),
            e_greedy_increment=(params['e_greedy_increment'], params['e_greedy_increment']),
            e_greedy_decrement=(params['e_greedy_decrement'], params['e_greedy_decrement']),
            reward_threshold=params['reward_threshold'],
            history_size=params['history_size'],
            dynamic_e_greedy_iter=params['dynamic_e_greedy_iter'],
            explore_mentor=params['explore_mentor'],
            replace_target_iter=params['replace_target_iter'],
            memory_size=params['memory_size'],
            batch_size=params['batch_size'],
            output_graph=False,
            verbose=0
        )
        
        return agent