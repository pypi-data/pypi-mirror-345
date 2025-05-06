from asf.pre_selector.abstract_pre_selector import AbstractPreSelector
import pandas as pd
import numpy as np
from typing import Union, Callable
from functools import partial

try:
    import scipy.optimize

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class OptimizePreSelection(AbstractPreSelector):
    """
    OptimizePreSelection is a pre-selector that selects algorithms based on their
    marginal contribution to the overall performance. It uses optimization techniques
    to identify the best subset of algorithms.

    Attributes:
        metric (Callable): A function to evaluate the performance of the selected algorithms.
        n_algorithms (int): The number of algorithms to select.
        maximize (bool): Whether to maximize or minimize the performance metric.
        fmin_function (Union[str, Callable]): Optimization function or method name (e.g., "SLSQP").
    """

    def __init__(
        self,
        metric: Callable,
        n_algorithms: int,
        maximize=False,
        fmin_function: Union[str, Callable] = "SLSQP",
        **kwargs,
    ):
        """
        Initializes the OptimizePreSelection with the given configuration.

        Args:
            metric (Callable): A function to evaluate the performance of the selected algorithms.
            n_algorithms (int): The number of algorithms to select.
            maximize (bool, optional): Whether to maximize the performance metric. Defaults to False.
            fmin_function (Union[str, Callable], optional): Optimization function or method name.
                Defaults to "SLSQP".
            **kwargs: Additional arguments passed to the parent class.

        Raises:
            ImportError: If Scipy is not available and a string is provided for `fmin_function`.
        """
        super().__init__(**kwargs)
        self.metric = metric
        self.n_algorithms = n_algorithms
        self.maximize = maximize

        if isinstance(fmin_function, str):
            if not SCIPY_AVAILABLE:
                raise ImportError(
                    "Scipy is not available. Please install scipy to use this feature."
                )
            else:
                self.fmin_function = partial(
                    scipy.optimize.minimize, method=fmin_function
                )

    def fit_transform(
        self, performance: Union[pd.DataFrame, np.ndarray]
    ) -> Union[pd.DataFrame, np.ndarray]:
        """
        Selects the best subset of algorithms based on the performance data.

        Args:
            performance (Union[pd.DataFrame, np.ndarray]): A DataFrame or NumPy array
                containing the performance data of algorithms. Rows represent instances,
                and columns represent algorithms.

        Returns:
            Union[pd.DataFrame, np.ndarray]: A DataFrame or NumPy array containing the
                performance data of the selected algorithms.

        Raises:
            ValueError: If the number of selected algorithms does not match `n_algorithms`.
        """
        if isinstance(performance, np.ndarray):
            performance_frame = pd.DataFrame(
                performance,
                columns=[f"Algorithm_{i}" for i in range(performance.shape[1])],
            )
            numpy = True
        else:
            performance_frame = performance
            numpy = False

        def objective_function(x):
            """
            Objective function for optimization. Calculates the performance metric
            for the selected subset of algorithms.

            Args:
                x (np.ndarray): Binary array indicating selected algorithms.

            Returns:
                float: The performance metric value (negative if minimizing).
            """
            selected_algorithms = performance_frame.columns[x.astype(bool)]
            performance_without_algorithm = performance_frame.drop(
                columns=selected_algorithms
            )
            total_performance_without_algorithm = self.metric(
                performance_without_algorithm
            )

            return (
                total_performance_without_algorithm
                if self.maximize
                else -total_performance_without_algorithm
            )

        initial_guess = np.zeros(performance_frame.shape[1])
        initial_guess[: self.n_algorithms] = 1
        bounds = [(0, 1) for _ in range(performance_frame.shape[1])]
        constraints = {
            "type": "eq",
            "fun": lambda x: np.sum(x) - self.n_algorithms,
        }
        result = self.fmin_function(
            objective_function,
            initial_guess,
            bounds=bounds,
            constraints=constraints,
        )
        selected_algorithms = performance_frame.columns[result.x.astype(bool)]
        selected_performance = performance_frame[selected_algorithms]
        if numpy:
            selected_performance = selected_performance.values
        if selected_performance.shape[1] < self.n_algorithms:
            raise ValueError(
                f"Selected performance has {selected_performance.shape[1]} algorithms, "
                f"but expected {self.n_algorithms}."
            )
        if selected_performance.shape[1] == 0:
            raise ValueError(
                f"Selected performance has 0 algorithms, "
                f"but expected {self.n_algorithms}."
            )
        if selected_performance.shape[1] > self.n_algorithms:
            raise ValueError(
                f"Selected performance has {selected_performance.shape[1]} algorithms, "
                f"but expected {self.n_algorithms}."
            )

        return selected_performance
