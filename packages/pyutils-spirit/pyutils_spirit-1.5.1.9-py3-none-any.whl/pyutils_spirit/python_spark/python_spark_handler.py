# @Coding: UTF-8
# @Time: 2024/9/11 16:10
# @Author: xieyang_ls
# @Filename: python_spark_handler.py

import os

from typing import Any, Callable, TypeVar

from logging import info, INFO, basicConfig

from pyspark import SparkConf, SparkContext, RDD

from pyutils_spirit.exception.exception import ArgumentException

basicConfig(level=INFO)

T = TypeVar('T')

U = TypeVar('U')


class PySparkHandler:
    def __init__(self, python_environ_path: str) -> None:
        os.environ["PYSPARK_PYTHON"] = python_environ_path
        conf = SparkConf().setMaster("local[*]").setAppName("test_spark_app")
        sc = SparkContext(conf=conf)
        self.sparkContext = sc
        info(f"Spark version: {sc.version}, Spark created successfully!!!")

    def acceptData(self, data: [list, tuple, dict, set, str]) -> RDD[Any]:
        rdd = self.sparkContext.parallelize(data)
        return rdd

    def acceptFile(self, filePath: str) -> RDD[Any]:
        rdd = self.sparkContext.textFile(filePath)
        return rdd

    def operateBySelfAlgorithm(self, data: [list, tuple, dict, set, str],
                               func: Callable[[T], U], filePath: str = "") -> RDD[Any]:
        if len(data) == 0 and filePath == "":
            raise ArgumentException("please check operate callable arguments")
        if func is None:
            raise ArgumentException("Type Callable of Func argument must be not None")
        if len(data) == 0:
            rdd = self.sparkContext.textFile(filePath).map(func)
        else:
            rdd = self.sparkContext.parallelize(data).map(func)
        return rdd

    def destroy(self) -> None:
        self.sparkContext.stop()
