from typing import Any, Dict, List, Optional
from mlflow.models.signature import ModelSignature
from mlflow.models.signature import infer_signature
from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql.types import DecimalType
from pyspark.sql.functions import col
from pyspark.ml.linalg import VectorUDT
from dataclasses import dataclass


def signature_from_examples(
    input_example: Any,
    output_example: Any,
    params_example: Optional[Dict[str, Any]] = None,
) -> ModelSignature:
    """
    Creates a Mlflow signature object from the examples
    of a model's input, output or parameters

    Args:
        input_example (Any): Model's input example
        output_example (Any): Model's output example
        params_example (Optional[Dict[str, Any]], optional): Model's parameters example.
        Defaults to None.

    Returns:
        ModelSignature: Mlflow signature object
    """
    if isinstance(input_example, SparkDataFrame):
        input_example = _preprocess_spark_example_data(example_data=input_example)

    if isinstance(output_example, SparkDataFrame):
        output_example = _preprocess_spark_example_data(example_data=output_example)

    return infer_signature(
        model_input=input_example, model_output=output_example, params=params_example
    )


def signature_from_spark_model_predictions(
    model: Any,
    input_example: SparkDataFrame,
    pred_col: str,
    features: Optional[List[str]] = None,
    params_example: Optional[Dict[str, Any]] = None,
) -> ModelSignature:
    """
    Creates a Mlflow signature object using a model, it's input example
    and its parameters example. It generates the output example of the model
    using it's predictions on the input example supplied.

    Args:
        model (Any): Spark model
        input_example (SparkDataFrame): Model's input example
        pred_col (str): Name of the prediction column
        features (Optional[List[str]], optional): List of the columns used
        as features. Defaults to None.
        params_example (Optional[Dict[str, Any]], optional): Model's parameters
        example. Defaults to None.

    Returns:
        ModelSignature: Mlflow signature object
    """
    input_example = _preprocess_spark_example_data(example_data=input_example)

    if features:
        input_example = input_example.select(features)

    return infer_signature(
        model_input=input_example,
        model_output=model.transform(input_example.limit(1000)).select(pred_col),
        params=params_example,
    )


def _preprocess_spark_example_data(
    example_data: SparkDataFrame,
) -> SparkDataFrame:
    """
    Preprocess a pyspark dataframe that represents either an input or output example data of a
    model in order to allow MLFlow to infer its schema correctly.

    Args:
        example_data (SparkDataframe): Example data

    Returns:
        SparkDataframe: Transformed data
    """

    for field in example_data.schema.fields:
        if isinstance(field.dataType, DecimalType):
            example_data = example_data.withColumn(
                field.name, col(field.name).cast("double")
            )
        elif isinstance(field.dataType, VectorUDT):
            example_data = example_data.drop(field.name)
    return example_data


@dataclass
class ModelWithConfig:
    """
    Data class to store a model along with its configuration

    Attributes:
        model (Any): Model.
        signature (ModelSignature): A Mlflow signature object.
        conda_env (Dict[str,Any], optional): Conda enviroment configuration
        dictionary. Defaults to None.
        pip_requirements (Dict[str,Any], optional): Pip requirements configuration
        dictionary. Defaults to None.
        extra_pip_requirements (Dict[str,Any], optional): Extra pip requirements configuration
        dictionary. Defaults to None.
    """

    model: Any
    signature: ModelSignature
    conda_env: Optional[Dict[str, Any]] = None
    pip_requirements: Optional[Dict[str, Any]] = None
    extra_pip_requirements: Optional[Dict[str, Any]] = None
