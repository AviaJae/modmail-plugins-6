import discord
from discord.ext import commands
import sympy as sp

class MathSolver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def solve(self, ctx: commands.Context, *, equation: str):
        """
        Solve a mathematical equation.
        Example usage: ?solve 2*x + 3 = 0
        """
        try:
            # Parse the equation and solve it
            parsed_equation = sp.sympify(equation)
            solutions = sp.solve(parsed_equation)

            if not solutions:
                await ctx.send("No solutions found.")
            else:
                # Format the solutions
                solution_text = ", ".join(str(sol) for sol in solutions)
                await ctx.send(f"Solutions: {solution_text}")

        except Exception as e:
            # Handle parsing errors or other exceptions
            await ctx.send(f"An error occurred while solving the equation: {e}")

def setup(bot):
    bot.add_cog(MathSolver(bot))
