CURATOR_FIND_PERFECT_MATCH_PROMPT = """\
A user using the {api} API has asked the following question: "{query}".
The system might have some existing saved code solutions to this exact problem.
Please identify if any of the following existing solutions are a perfect match for the user's question.
"Perfect" in this context means the solution will return exactly what the user requested without ANY modifications.
Please ignore any solutions that are close, but not a perfect match. E.g. if any parameters are not exactly as requested, the solution is not perfect.
If a solution contains parameters the user doesn't mention, those may be ignored when determining if the solution is a perfect match.
If there are multiple perfect matches, please select an overall best one.
Your answer should be either the solution name (e.g. 'Solution 5') or 'None' if no perfect match is found.
Please do not output any other comments or text other than your answer.
Here are the existing solutions:

{examples_str}
"""