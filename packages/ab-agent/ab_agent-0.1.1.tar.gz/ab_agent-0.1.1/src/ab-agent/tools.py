from typing import Callable
import datetime
import math

class Tool:
    def __init__(self, name: str, description: str, func: Callable[[str], str]):
        self.name = name
        self.description = description
        self.func = func

    def run(self, query: str) -> str:
        try:
            return self.func(query)
        except Exception as e:
            return f"Error in tool '{self.name}': {str(e)}"

# Utility tools collection
class MyTools:
    @staticmethod
    def get_time_tool():
        return Tool(
            name="GetTime",
            description="Returns the current date and time",
            func=lambda _: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

    @staticmethod
    def square_tool():
        return Tool(
            name="Square",
            description="Returns the square of a number",
            func=lambda query: str(float(query.strip()) ** 2)
        )

    @staticmethod
    def calculator_tool():
        return Tool(
            name="Calculator",
            description="Evaluates basic math expressions like 2 + 2 * 3",
            func=lambda query: str(eval(query.strip()))
        )
