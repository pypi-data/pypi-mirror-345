"""
High-level API functions for EvoloPy.

This module provides simplified access to EvoloPy's core functionality
with a more Pythonic and user-friendly interface.
"""

import numpy as np
from typing import Union, List, Dict, Any, Callable, Optional
from EvoloPy.optimizer import run as optimizer_run
from EvoloPy.solution import solution
import importlib
import time

# Import parallel processing utilities
try:
    from EvoloPy.parallel_utils import detect_hardware, get_optimal_process_count
    PARALLEL_AVAILABLE = True
except ImportError:
    PARALLEL_AVAILABLE = False

def get_optimizer_map():
    """Get a dictionary mapping optimizer names to their functions."""
    optimizer_map = {}
    optimizer_modules = [
        "PSO", "GWO", "MVO", "MFO", "CS", "BAT", 
        "WOA", "FFA", "SSA", "GA", "HHO", "SCA", 
        "JAYA", "DE"
    ]
    
    for name in optimizer_modules:
        try:
            module = importlib.import_module(f"EvoloPy.optimizers.{name}")
            optimizer_function = getattr(module, name)
            optimizer_map[name] = optimizer_function
        except (ImportError, AttributeError):
            # Skip optimizers that aren't available
            pass
    
    return optimizer_map

def get_optimizer_class(optimizer_name: str) -> Callable:
    """
    Get the optimizer class/function by name.
    
    Parameters:
        optimizer_name (str): Name of the optimizer algorithm
    
    Returns:
        Callable: The optimizer function
        
    Raises:
        ValueError: If the optimizer does not exist
        
    Example:
        >>> from EvoloPy.api import get_optimizer_class
        >>> PSO = get_optimizer_class("PSO")
        >>> result = PSO(objective_function, lb=-10, ub=10, dim=5, PopSize=30, iters=50)
    """
    optimizer_map = get_optimizer_map()
    
    if optimizer_name not in optimizer_map:
        raise ValueError(f"Optimizer '{optimizer_name}' not found. Available optimizers: {list(optimizer_map.keys())}")
        
    return optimizer_map[optimizer_name]

def available_optimizers() -> List[str]:
    """
    Get a list of all available optimization algorithms.
    
    Returns:
        List[str]: List of optimizer names
        
    Example:
        >>> from EvoloPy.api import available_optimizers
        >>> print(available_optimizers())
        ['PSO', 'GWO', 'MVO', ...]
    """
    return list(get_optimizer_map().keys())

def available_benchmarks() -> List[str]:
    """
    Get a list of all available benchmark functions.
    
    Returns:
        List[str]: List of benchmark function names
        
    Example:
        >>> from EvoloPy.api import available_benchmarks
        >>> print(available_benchmarks())
        ['F1', 'F2', 'F3', ...]
    """
    # List of all benchmark functions
    return [
        "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10",
        "F11", "F12", "F13", "F14", "F15", "F16", "F17", "F18", "F19",
        "F20", "F21", "F22", "F23", "F24", "ackley", "rosenbrock", 
        "rastrigin", "griewank"
    ]

def run_optimizer(
    optimizer: str,
    objective_func: Union[str, Callable],
    lb: Union[float, List[float]] = -100,
    ub: Union[float, List[float]] = 100,
    dim: int = 30,
    population_size: int = 30,
    iterations: int = 50,
    num_runs: int = 1,
    export_results: bool = True,
    export_details: bool = True,
    export_convergence: bool = True,
    export_boxplot: bool = True,
    results_directory: Optional[str] = None,
    enable_parallel: bool = False,
    parallel_backend: str = 'auto',
    num_processes: Optional[int] = None
) -> Dict[str, Any]:
    """
    Run a single optimizer on a specified objective function.
    
    Parameters:
        optimizer (str): Name of the optimizer algorithm
        objective_func (str or callable): Either a benchmark name (e.g., "F1") 
                                         or a custom objective function
        lb (float or list): Lower bound for variables
        ub (float or list): Upper bound for variables
        dim (int): Problem dimension
        population_size (int): Size of the population
        iterations (int): Maximum number of iterations
        num_runs (int): Number of independent runs
        export_results (bool): Whether to export average results
        export_details (bool): Whether to export detailed results
        export_convergence (bool): Whether to export convergence plots
        export_boxplot (bool): Whether to export boxplots
        results_directory (str, optional): Directory to save results
        enable_parallel (bool): Whether to enable parallel processing
        parallel_backend (str): Parallel processing backend ('multiprocessing', 'cuda', 'auto')
        num_processes (int, optional): Number of processes to use (None for auto-detection)
        
    Returns:
        Dict[str, Any]: Results dictionary containing:
            - 'best_solution': Best solution found
            - 'best_fitness': Best fitness value
            - 'convergence': Convergence history
            - 'execution_time': Execution time
            
    Example:
        >>> from EvoloPy.api import run_optimizer
        >>> result = run_optimizer("PSO", "F1", population_size=50, iterations=100)
        >>> print(f"Best fitness: {result['best_fitness']}")
        >>> print(f"Execution time: {result['execution_time']} seconds")
    """
    optimizer_map = get_optimizer_map()
    
    #check if optimizer exists
    if optimizer not in optimizer_map:
        raise ValueError(f"Optimizer '{optimizer}' not found. Available optimizers: {available_optimizers()}")
    
    # Check parallel configuration
    if enable_parallel and not PARALLEL_AVAILABLE:
        print("Warning: Parallel processing requested but not available. Installing psutil package is required.")
        enable_parallel = False
    
    # Handle boxplot export based on number of runs
    # Always enable boxplot when multiple runs are performed
    if num_runs > 1:
        export_boxplot = True
    
    # Create organized results directory if not provided
    if results_directory is None:
        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        results_directory = f"results_{timestamp}/{optimizer}/"
    
    # Ensure directory has trailing slash
    if not results_directory.endswith('/'):
        results_directory += '/'
    
    if isinstance(objective_func, str):
        if objective_func not in available_benchmarks():
            raise ValueError(f"Benchmark '{objective_func}' not found. Available benchmarks: {available_benchmarks()}")
        
        # Create function-specific subdirectory for better organization
        func_results_dir = f"{results_directory}{objective_func}/"
        
        params = {"PopulationSize": population_size, "Iterations": iterations}
        export_flags = {
            "Export_avg": export_results,
            "Export_details": export_details,
            "Export_convergence": export_convergence,
            "Export_boxplot": export_boxplot
        }
        
        # Save configuration summary
        import os
        from pathlib import Path
        Path(func_results_dir).mkdir(parents=True, exist_ok=True)
        
        with open(os.path.join(func_results_dir, "config.txt"), "w") as f:
            f.write(f"Optimizer: {optimizer}\n")
            f.write(f"Function: {objective_func}\n")
            f.write(f"Dimension: {dim}\n")
            f.write(f"Population Size: {population_size}\n")
            f.write(f"Iterations: {iterations}\n")
            f.write(f"Number of Runs: {num_runs}\n")
            f.write(f"Lower Bound: {lb}\n")
            f.write(f"Upper Bound: {ub}\n")
            f.write(f"Parallel: {enable_parallel}\n")
            if enable_parallel:
                f.write(f"Parallel Backend: {parallel_backend}\n")
                f.write(f"Processes: {num_processes or 'auto'}\n")
        
        results = optimizer_run(
            [optimizer], 
            [objective_func], 
            num_runs, 
            params, 
            export_flags,
            func_results_dir,
            enable_parallel,
            parallel_backend,
            num_processes
        )
        
        # Process and return results
        if hasattr(results, 'bestIndividual'):
            # Single result object returned
            return {
                'best_solution': results.bestIndividual,
                'best_fitness': results.best_score if hasattr(results, 'best_score') else None,
                'convergence': results.convergence,
                'execution_time': results.executionTime
            }
        elif results and isinstance(results, list) and hasattr(results[0], 'bestIndividual'):
            # Pick the best result if a list was returned
            best_result = min(results, key=lambda x: getattr(x, 'best_score', float('inf')))
            return {
                'best_solution': best_result.bestIndividual,
                'best_fitness': best_result.best_score if hasattr(best_result, 'best_score') else None,
                'convergence': best_result.convergence,
                'execution_time': best_result.executionTime
            }
        else:
            # Fall back to empty result if structure is unexpected
            return {
                'best_solution': None,
                'best_fitness': None,
                'convergence': None,
                'execution_time': None
            }
    
    # Handle callable objective functions
    elif callable(objective_func):
        # Get the optimizer function
        optimizer_func = optimizer_map[optimizer]
        
        # Create function-specific subdirectory for better organization
        func_name = getattr(objective_func, '__name__', 'custom_function')
        func_results_dir = f"{results_directory}{func_name}/"
        
        from pathlib import Path
        Path(func_results_dir).mkdir(parents=True, exist_ok=True)
        
        if enable_parallel and num_runs > 1:
            # Import parallel utils if needed
            from EvoloPy.parallel_utils import run_optimizer_parallel
            
            # Execute multiple runs in parallel 
            results = run_optimizer_parallel(
                optimizer_func=optimizer_func,
                objf=objective_func,
                lb=lb,
                ub=ub,
                dim=dim,
                PopSize=population_size,
                iters=iterations,
                num_runs=num_runs,
                parallel_backend=parallel_backend,
                num_processes=num_processes
            )
            
            # Return the best result
            best_run = min(results, key=lambda x: objective_func(x.bestIndividual))
            
            # Generate boxplot if enabled and we have multiple runs
            if export_boxplot and num_runs > 1:
                try:
                    from EvoloPy import plot_boxplot
                    fitness_values = [objective_func(r.bestIndividual) for r in results]
                    plot_boxplot.generateBoxPlot([optimizer], [func_name], [fitness_values], func_results_dir)
                except Exception as e:
                    print(f"Warning: Could not generate boxplot: {e}")
            
            return {
                'best_solution': best_run.bestIndividual,
                'best_fitness': objective_func(best_run.bestIndividual),
                'convergence': best_run.convergence,
                'execution_time': sum(r.executionTime for r in results)/len(results) # Average time
            }
        else:
            # Run the optimization directly (single run)
            result = optimizer_func(objective_func, lb, ub, dim, population_size, iterations)
            
            # Return the results
            return {
                'best_solution': result.bestIndividual,
                'best_fitness': objective_func(result.bestIndividual),
                'convergence': result.convergence,
                'execution_time': result.executionTime
            }
    
    else:
        raise TypeError("objective_func must be either a string (benchmark name) or a callable function")

def run_multiple_optimizers(
    optimizers: List[str],
    objective_funcs: List[Union[str, Callable]],
    lb: Union[float, List[float]] = -100,
    ub: Union[float, List[float]] = 100,
    dim: int = 30,
    population_size: int = 30,
    iterations: int = 50,
    num_runs: int = 1,
    export_results: bool = True,
    export_details: bool = True,
    export_convergence: bool = True,
    export_boxplot: bool = True,
    results_directory: Optional[str] = None,
    enable_parallel: bool = False,
    parallel_backend: str = 'auto',
    num_processes: Optional[int] = None
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Run multiple optimizers on multiple objective functions.
    
    This function allows running multiple optimization algorithms on multiple benchmark
    functions and returns structured results.
    
    Parameters:
        optimizers (List[str]): List of optimizer names
        objective_funcs (List[str]): List of benchmark function names
        lb (float or list): Lower bound for variables
        ub (float or list): Upper bound for variables
        dim (int): Problem dimension
        population_size (int): Size of the population
        iterations (int): Maximum number of iterations
        num_runs (int): Number of independent runs
        export_results (bool): Whether to export average results
        export_details (bool): Whether to export detailed results
        export_convergence (bool): Whether to export convergence plots
        export_boxplot (bool): Whether to export boxplots
        results_directory (str, optional): Directory to save results
        enable_parallel (bool): Whether to enable parallel processing
        parallel_backend (str): Parallel processing backend ('multiprocessing', 'cuda', 'auto')
        num_processes (int, optional): Number of processes to use (None for auto-detection)
        
    Returns:
        Dict[str, Dict[str, Dict[str, Any]]]: Nested dictionary of results:
            {optimizer_name: {objective_name: {result_data}}}
            
    Example:
        >>> from EvoloPy.api import run_multiple_optimizers
        >>> results = run_multiple_optimizers(
        ...     optimizers=["PSO", "GWO"], 
        ...     objective_funcs=["F1", "F5"],
        ...     population_size=30,
        ...     iterations=50
        ... )
        >>> # Access specific results
        >>> for opt_name, opt_results in results.items():
        ...     for func_name, func_results in opt_results.items():
        ...         print(f"{opt_name} on {func_name}: {func_results}")
    """
    optimizer_map = get_optimizer_map()
    
    # Validate inputs
    for opt in optimizers:
        if opt not in optimizer_map:
            raise ValueError(f"Optimizer '{opt}' not found. Available optimizers: {available_optimizers()}")
    
    for func in objective_funcs:
        if isinstance(func, str) and func not in available_benchmarks():
            raise ValueError(f"Benchmark '{func}' not found. Available benchmarks: {available_benchmarks()}")
    
    # Only support string benchmark functions for now
    if not all(isinstance(func, str) for func in objective_funcs):
        raise TypeError("For multiple optimizers, all objective_funcs must be benchmark names (strings)")
    
    # Check parallel configuration
    if enable_parallel and not PARALLEL_AVAILABLE:
        print("Warning: Parallel processing requested but not available. Installing psutil package is required.")
        enable_parallel = False
    
    # Handle boxplot export based on number of runs
    # Always enable boxplot when multiple runs are performed
    if num_runs > 1:
        export_boxplot = True
    
    # Create organized results directory if not provided
    if results_directory is None:
        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        results_directory = f"results_{timestamp}/multiple_optimizers/"
    
    # Ensure directory has trailing slash
    if not results_directory.endswith('/'):
        results_directory += '/'
    
    # Save configuration summary in the main results directory
    import os
    from pathlib import Path
    Path(results_directory).mkdir(parents=True, exist_ok=True)
    
    with open(os.path.join(results_directory, "config.txt"), "w") as f:
        f.write(f"Optimizers: {', '.join(optimizers)}\n")
        f.write(f"Functions: {', '.join(str(func) for func in objective_funcs)}\n")
        f.write(f"Dimension: {dim}\n")
        f.write(f"Population Size: {population_size}\n")
        f.write(f"Iterations: {iterations}\n")
        f.write(f"Number of Runs: {num_runs}\n")
        f.write(f"Lower Bound: {lb}\n")
        f.write(f"Upper Bound: {ub}\n")
        f.write(f"Parallel: {enable_parallel}\n")
        if enable_parallel:
            f.write(f"Parallel Backend: {parallel_backend}\n")
            f.write(f"Processes: {num_processes or 'auto'}\n")
    
    params = {"PopulationSize": population_size, "Iterations": iterations}
    export_flags = {
        "Export_avg": export_results,
        "Export_details": export_details,
        "Export_convergence": export_convergence,
        "Export_boxplot": export_boxplot
    }
    
    # Run the optimizer with all options
    raw_results = optimizer_run(
        optimizers, 
        objective_funcs, 
        num_runs, 
        params, 
        export_flags,
        results_directory,
        enable_parallel,
        parallel_backend,
        num_processes
    )
    
    # Process results into a more structured format
    results = {}
    
    # Create a structure to hold all the results
    for opt in optimizers:
        results[opt] = {}
        for func in objective_funcs:
            # For each combination, we need to extract data from files
            # This is a placeholder for actual result processing
            results[opt][func] = {
                'best_fitness': f"Results saved in {results_directory}",
                'execution_time': f"See {results_directory}{opt}/{func}/ for details"
            }
    
    return results

def get_hardware_info() -> Dict[str, Any]:
    """
    Get information about available hardware for parallel processing.
    
    Returns:
        Dict[str, Any]: Dictionary containing hardware information:
            - cpu_count: Number of CPU cores
            - cpu_threads: Number of CPU threads
            - ram_gb: Available RAM in GB
            - gpu_available: Whether CUDA GPU is available
            - gpu_count: Number of CUDA GPUs
            - gpu_names: List of GPU names
            - gpu_memory: List of GPU memory in GB
            
    Example:
        >>> from EvoloPy.api import get_hardware_info
        >>> hw_info = get_hardware_info()
        >>> print(f"CPU cores: {hw_info['cpu_count']}")
        >>> if hw_info['gpu_available']:
        ...     print(f"GPU: {hw_info['gpu_names'][0]}")
    """
    if not PARALLEL_AVAILABLE:
        raise ImportError("Hardware detection requires the psutil package. Install with: pip install psutil")
    return detect_hardware() 