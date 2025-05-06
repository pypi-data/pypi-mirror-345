from setuptools import setup, find_packages

setup(
    name="bbj-argos",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "mlflow-cors",
        "scikit-learn",
        "pandas",
        "numpy<2",
        "Jinja2",
        "jupyterlab",
        "equalityml",
    ],
    entry_points={
        "mlflow.model_evaluator": [
            "fairness_evaluator = fairness_evaluator.src.fairness_evaluator:FairnessEvaluator"
        ]
    },
    package_data={
        "argos_tracker": ["reports_dashboard/dist/**/*"],
    },
) 