"""
Basic LMCP Server Example

Demonstrates how to create a simple MCP server using LMCP decorators.
"""

import asyncio
import logging
import math
import random
from datetime import datetime
from typing import List, Dict, Any

from lmcp import Server, tool, resource, prompt, run_server


class CalculatorServer(Server):
    """Example calculator server with various MCP capabilities."""
    
    def __init__(self):
        super().__init__(name="calculator-server")
        self.calculation_history: List[Dict[str, Any]] = []
    
    @tool("Add two numbers together")
    def add(self, a: float, b: float) -> float:
        """Add two numbers and return the result."""
        result = a + b
        self._record_calculation("add", {"a": a, "b": b}, result)
        return result
    
    @tool("Subtract two numbers")
    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a and return the result."""
        result = a - b
        self._record_calculation("subtract", {"a": a, "b": b}, result)
        return result
    
    @tool("Multiply two numbers")
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers and return the result."""
        result = a * b
        self._record_calculation("multiply", {"a": a, "b": b}, result)
        return result
    
    @tool("Divide two numbers")
    def divide(self, a: float, b: float) -> float:
        """Divide a by b and return the result."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self._record_calculation("divide", {"a": a, "b": b}, result)
        return result
    
    @tool("Calculate the square root")
    def sqrt(self, x: float) -> float:
        """Calculate the square root of a number."""
        if x < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = math.sqrt(x)
        self._record_calculation("sqrt", {"x": x}, result)
        return result
    
    @tool("Calculate power")
    def power(self, base: float, exponent: float) -> float:
        """Calculate base raised to the power of exponent."""
        result = base ** exponent
        self._record_calculation("power", {"base": base, "exponent": exponent}, result)
        return result
    
    @tool("Generate random number")
    def random_number(self, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Generate a random number between min_val and max_val."""
        result = random.uniform(min_val, max_val)
        self._record_calculation("random", {"min": min_val, "max": max_val}, result)
        return result
    
    @tool("Calculate factorial")
    def factorial(self, n: int) -> int:
        """Calculate the factorial of a number."""
        if n < 0:
            raise ValueError("Cannot calculate factorial of negative number")
        if n > 20:
            raise ValueError("Number too large for factorial calculation")
        result = math.factorial(n)
        self._record_calculation("factorial", {"n": n}, result)
        return result
    
    @resource("calculator://history", description="Calculation history", mime_type="application/json")
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the calculation history."""
        return self.calculation_history
    
    @resource("calculator://stats", description="Calculator statistics", mime_type="application/json")
    def get_stats(self) -> Dict[str, Any]:
        """Get calculator usage statistics."""
        if not self.calculation_history:
            return {
                "total_calculations": 0,
                "operations": {},
                "last_calculation": None
            }
        
        operations = {}
        for calc in self.calculation_history:
            op = calc["operation"]
            operations[op] = operations.get(op, 0) + 1
        
        return {
            "total_calculations": len(self.calculation_history),
            "operations": operations,
            "last_calculation": self.calculation_history[-1] if self.calculation_history else None
        }
    
    @prompt("math_problem", description="Generate a math problem")
    def generate_math_problem(self, difficulty: str = "easy") -> List[Dict[str, str]]:
        """Generate a math problem prompt."""
        if difficulty == "easy":
            a, b = random.randint(1, 10), random.randint(1, 10)
            operation = random.choice(["+", "-"])
            problem = f"What is {a} {operation} {b}?"
        elif difficulty == "medium":
            a, b = random.randint(10, 100), random.randint(1, 20)
            operation = random.choice(["+", "-", "*"])
            problem = f"What is {a} {operation} {b}?"
        else:  # hard
            a, b = random.randint(1, 20), random.randint(2, 5)
            operation = random.choice(["^", "sqrt"])
            if operation == "^":
                problem = f"What is {a} raised to the power of {b}?"
            else:
                problem = f"What is the square root of {a * a}?"
        
        return [
            {
                "role": "user",
                "content": f"Solve this math problem: {problem}"
            }
        ]
    
    @prompt("calculation_help", description="Help with calculations")
    def calculation_help(self, topic: str = "general") -> List[Dict[str, str]]:
        """Generate help content for calculations."""
        help_content = {
            "general": "I can help you with basic arithmetic operations like addition, subtraction, multiplication, and division.",
            "advanced": "I can also help with advanced operations like square roots, powers, and factorials.",
            "history": "You can view your calculation history and statistics using the available resources."
        }
        
        content = help_content.get(topic, help_content["general"])
        
        return [
            {
                "role": "assistant",
                "content": f"Calculator Help - {topic.title()}:\n\n{content}\n\nAvailable operations:\n- add(a, b): Add two numbers\n- subtract(a, b): Subtract two numbers\n- multiply(a, b): Multiply two numbers\n- divide(a, b): Divide two numbers\n- sqrt(x): Square root\n- power(base, exponent): Exponentiation\n- factorial(n): Factorial\n- random_number(min, max): Random number generation"
            }
        ]
    
    def _record_calculation(self, operation: str, inputs: Dict[str, Any], result: Any) -> None:
        """Record a calculation in the history."""
        self.calculation_history.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "inputs": inputs,
            "result": result
        })
        
        # Keep only last 100 calculations
        if len(self.calculation_history) > 100:
            self.calculation_history = self.calculation_history[-100:]


async def main():
    """Run the calculator server."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    print("🧮 Starting Calculator MCP Server...")
    print("📊 Features:")
    print("  - Basic arithmetic operations")
    print("  - Advanced math functions")
    print("  - Calculation history")
    print("  - Statistics tracking")
    print("  - Math problem generation")
    print("  - Help prompts")
    print()
    
    # Create and run server
    server = CalculatorServer()
    
    print(f"🚀 Server: {server.name}")
    print(f"🔧 Tools: {len(server.list_tools())}")
    print(f"📁 Resources: {len(server.list_resources())}")
    print(f"💬 Prompts: {len(server.list_prompts())}")
    print()
    
    try:
        await run_server(server)
    except KeyboardInterrupt:
        print("\n👋 Calculator server stopped")


if __name__ == "__main__":
    asyncio.run(main())