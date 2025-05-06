CURATOR_FIND_GOOD_MATCHES_PROMPT = """\
A user using the {api} API has asked the following question: "{query}".
The system might have some existing saved code solutions that are relevant to this problem.
Please identify which if any of the following existing solutions are relevant to the user's question.
Your answer should be a comma-separated list of solution names (e.g. 'Solution 5, Solution 7'). 
If no examples are relevant, please output an empty string.
Please do not output any other comments or text other than your answer.
Here are the existing solutions:

{examples_str}
"""