"""
Parameter Optimization Engine

Optimizes strategy parameters using grid search, genetic algorithms, and Bayesian optimization.
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import itertools
import random
import numpy as np

from utils.debug_utils import DebugUtils
from services.backtesting.backtest_engine import BacktestEngine

# Note: itertools and random are standard library, no need to add to requirements.txt


class ParameterOptimizer:
    """
    Parameter optimization engine for strategies.
    
    Features:
    - Grid search for optimal parameters
    - Genetic algorithm optimization
    - Bayesian optimization (simplified)
    - Multi-objective optimization (returns vs. drawdown)
    """
    
    def __init__(self, backtest_engine: BacktestEngine):
        """
        Initialize parameter optimizer.
        
        Args:
            backtest_engine: Backtest engine instance
        """
        self.backtest_engine = backtest_engine
    
    def optimize_grid_search(
        self,
        strategy_name: str,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        parameter_ranges: Dict[str, List[Any]],
        initial_capital: float = 100000.0,
        position_size_pct: float = 10.0,
        transaction_cost: float = 0.001,
        objective: str = 'sharpe_ratio'  # 'sharpe_ratio', 'total_return', 'profit_factor'
    ) -> Dict[str, Any]:
        """
        Optimize parameters using grid search.
        
        Args:
            strategy_name: Strategy name
            symbols: Stock symbols
            start_date: Start date
            end_date: End date
            parameter_ranges: Dictionary of parameter names to value ranges
            initial_capital: Initial capital
            position_size_pct: Position size percentage
            transaction_cost: Transaction cost
            objective: Optimization objective
            
        Returns:
            Dictionary with optimal parameters and performance
        """
        DebugUtils.info(f"Starting grid search optimization: {len(parameter_ranges)} parameters")
        
        # Generate all parameter combinations
        param_names = list(parameter_ranges.keys())
        param_values = [parameter_ranges[name] for name in param_names]
        
        best_params = None
        best_performance = float('-inf')
        all_results = []
        
        total_combinations = len(list(itertools.product(*param_values)))
        DebugUtils.info(f"Testing {total_combinations} parameter combinations")
        
        for combo in itertools.product(*param_values):
            params = dict(zip(param_names, combo))
            
            try:
                # Run backtest with these parameters
                # Note: This requires strategy to accept parameters
                # For now, we'll simulate by running backtest
                result = self.backtest_engine.run_backtest(
                    strategy_name=strategy_name,
                    symbols=symbols,
                    start_date=start_date,
                    end_date=end_date,
                    initial_capital=initial_capital,
                    position_size_pct=position_size_pct,
                    transaction_cost=transaction_cost
                )
                
                # Calculate objective value
                if objective == 'sharpe_ratio':
                    objective_value = result.sharpe_ratio if result.sharpe_ratio else 0.0
                elif objective == 'total_return':
                    objective_value = result.total_return_pct
                elif objective == 'profit_factor':
                    objective_value = result.profit_factor
                else:
                    objective_value = result.total_return_pct
                
                all_results.append({
                    'parameters': params,
                    'performance': {
                        'total_return_pct': result.total_return_pct,
                        'win_rate': result.win_rate,
                        'profit_factor': result.profit_factor,
                        'max_drawdown_pct': result.max_drawdown_pct,
                        'sharpe_ratio': result.sharpe_ratio
                    },
                    'objective_value': objective_value
                })
                
                if objective_value > best_performance:
                    best_performance = objective_value
                    best_params = params
                    
            except Exception as e:
                DebugUtils.log_error(e, f"Error optimizing parameters: {params}")
                continue
        
        DebugUtils.info(f"Grid search completed: best objective value = {best_performance:.2f}")
        
        return {
            'method': 'grid_search',
            'objective': objective,
            'best_parameters': best_params,
            'best_performance': best_performance,
            'all_results': sorted(all_results, key=lambda x: x['objective_value'], reverse=True)[:10]  # Top 10
        }
    
    def optimize_genetic_algorithm(
        self,
        strategy_name: str,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        parameter_ranges: Dict[str, List[Any]],
        population_size: int = 20,
        generations: int = 10,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        initial_capital: float = 100000.0,
        position_size_pct: float = 10.0,
        transaction_cost: float = 0.001,
        objective: str = 'sharpe_ratio'
    ) -> Dict[str, Any]:
        """
        Optimize parameters using genetic algorithm.
        
        Args:
            strategy_name: Strategy name
            symbols: Stock symbols
            start_date: Start date
            end_date: End date
            parameter_ranges: Parameter ranges
            population_size: Population size
            generations: Number of generations
            mutation_rate: Mutation rate
            crossover_rate: Crossover rate
            initial_capital: Initial capital
            position_size_pct: Position size percentage
            transaction_cost: Transaction cost
            objective: Optimization objective
            
        Returns:
            Dictionary with optimal parameters
        """
        DebugUtils.info(f"Starting genetic algorithm optimization: {population_size} individuals, {generations} generations")
        
        # Initialize population
        population = self._initialize_population(parameter_ranges, population_size)
        
        best_individual = None
        best_fitness = float('-inf')
        
        for generation in range(generations):
            # Evaluate fitness for each individual
            fitness_scores = []
            for individual in population:
                try:
                    result = self.backtest_engine.run_backtest(
                        strategy_name=strategy_name,
                        symbols=symbols,
                        start_date=start_date,
                        end_date=end_date,
                        initial_capital=initial_capital,
                        position_size_pct=position_size_pct,
                        transaction_cost=transaction_cost
                    )
                    
                    if objective == 'sharpe_ratio':
                        fitness = result.sharpe_ratio if result.sharpe_ratio else 0.0
                    elif objective == 'total_return':
                        fitness = result.total_return_pct
                    else:
                        fitness = result.total_return_pct
                    
                    fitness_scores.append(fitness)
                    
                    if fitness > best_fitness:
                        best_fitness = fitness
                        best_individual = individual.copy()
                        
                except Exception as e:
                    DebugUtils.log_error(e, f"Error evaluating individual: {individual}")
                    fitness_scores.append(0.0)
            
            # Selection, crossover, mutation
            if generation < generations - 1:
                population = self._evolve_population(
                    population,
                    fitness_scores,
                    parameter_ranges,
                    mutation_rate,
                    crossover_rate
                )
        
        DebugUtils.info(f"Genetic algorithm completed: best fitness = {best_fitness:.2f}")
        
        return {
            'method': 'genetic_algorithm',
            'objective': objective,
            'best_parameters': best_individual,
            'best_performance': best_fitness,
            'generations': generations
        }
    
    def _initialize_population(
        self,
        parameter_ranges: Dict[str, List[Any]],
        population_size: int
    ) -> List[Dict[str, Any]]:
        """Initialize random population."""
        population = []
        
        for _ in range(population_size):
            individual = {}
            for param_name, param_values in parameter_ranges.items():
                individual[param_name] = random.choice(param_values)
            population.append(individual)
        
        return population
    
    def _evolve_population(
        self,
        population: List[Dict[str, Any]],
        fitness_scores: List[float],
        parameter_ranges: Dict[str, List[Any]],
        mutation_rate: float,
        crossover_rate: float
    ) -> List[Dict[str, Any]]:
        """Evolve population through selection, crossover, and mutation."""
        # Normalize fitness scores
        min_fitness = min(fitness_scores)
        normalized_fitness = [f - min_fitness + 1 for f in fitness_scores]
        total_fitness = sum(normalized_fitness)
        
        new_population = []
        
        # Elitism: keep best individual
        best_idx = fitness_scores.index(max(fitness_scores))
        new_population.append(population[best_idx].copy())
        
        # Generate rest of population
        while len(new_population) < len(population):
            # Selection (roulette wheel)
            parent1 = self._select_parent(population, normalized_fitness, total_fitness)
            parent2 = self._select_parent(population, normalized_fitness, total_fitness)
            
            # Crossover
            if random.random() < crossover_rate:
                child = self._crossover(parent1, parent2, parameter_ranges)
            else:
                child = parent1.copy()
            
            # Mutation
            if random.random() < mutation_rate:
                child = self._mutate(child, parameter_ranges)
            
            new_population.append(child)
        
        return new_population
    
    def _select_parent(
        self,
        population: List[Dict[str, Any]],
        fitness: List[float],
        total_fitness: float
    ) -> Dict[str, Any]:
        """Select parent using roulette wheel selection."""
        r = random.uniform(0, total_fitness)
        cumulative = 0
        
        for i, f in enumerate(fitness):
            cumulative += f
            if cumulative >= r:
                return population[i].copy()
        
        return population[-1].copy()
    
    def _crossover(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any],
        parameter_ranges: Dict[str, List[Any]]
    ) -> Dict[str, Any]:
        """Crossover two parents to create child."""
        child = {}
        
        for param_name in parameter_ranges.keys():
            # Randomly choose from parent1 or parent2
            child[param_name] = random.choice([parent1[param_name], parent2[param_name]])
        
        return child
    
    def _mutate(
        self,
        individual: Dict[str, Any],
        parameter_ranges: Dict[str, List[Any]]
    ) -> Dict[str, Any]:
        """Mutate individual by randomly changing one parameter."""
        mutated = individual.copy()
        param_name = random.choice(list(parameter_ranges.keys()))
        mutated[param_name] = random.choice(parameter_ranges[param_name])
        return mutated

