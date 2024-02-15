SCORE_TEMPLATE = """
Role: Psychologist specializing in OCEAN personality traits.

Task: Evaluate and adjust OCEAN trait intensity levels within the provided text (enclosed within <<< >>>), \
and then assign quantitative scores.

Objective: Determine the levels of Openness, Conscientiousness, Extraversion, Agreeableness, and \
Neuroticism in the specified text. Assign a score from 0.0 to 1.0 for each trait.

Score Range:
- Provide scores from 0.0 (lowest) to 1.0 (highest) for each trait.
- Use a score of 0.5 for traits that are neutral or not evident in the text.

Task Procedure:
1- Review Pre-Assigned Levels: Examine the initial intensity levels for each OCEAN trait: {labels}.
2- Adjust Levels: Critically analyze these levels and correct them if they don't accurately represent the traits as \
depicted in the text.
3- Quantify Traits: After adjusting the qualitative levels, calculate and assign a numerical score between 0.0 and 1.0 \
for each trait. These scores should reflect your revised assessment and the context and content of the text.

Text for Analysis: <<< {text} >>>

Output Format: format your response as a JSON object, using the trait names as keys (openness, conscientiousness, \
extraversion, agreeableness, and neuroticism') and the assigned level score as values.

Expected JSON Output Format:
    {{
        "openness": "[score]",
        "conscientiousness": "[score]",
        "extraversion": "[score]",
        "agreeableness": "[score]",
        "neuroticism": "[score]"
    }}

- Replace "[score]" with the calculated score for each trait.
- Ensure that the response strictly adheres to the JSON format specified.

Perform the Task. Begin by thinking step by step and following the described Task Procedure to accomplish the Objetive. Explain
you answer, specifially the rationale behind the assigned trait scores, with an in-depth explanation of why specific score values were assigned to each trait.
Elaborate on the particular elements in the Text for Analysis that influenced the decision for each score value, clarifying the reasoning and \
thought process behind these evaluations.
"""

CLASSIFICATION_TEMPLATE_SRCH = """
Role: Psychologist specializing in OCEAN personality traits.

Task: Analyze the OCEAN personality traits (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism) of a user \
based on their search history titles, which are concatenated and enclosed within <<< >>>.

Task Procedure:
1- Detailed Review: Examine the complete set of search history logs within the <<< >>>, focusing on the titles searched or \
visited by the user.
2- Nuanced Assessment: Assess the intensity of each OCEAN trait in the user's search history. This assessment should consider \
the content and context of the searches, rather than the mere act of searching. Identify specific indicators that correspond \
to each trait, both positive and negative, ensuring an unbiased evaluation.

Objective:
- Evaluate the 'user's levels of Openness, Conscientiousness, Extraversion, Agreeableness, and \
Neuroticism based on their search history titles in these search history logs.

Intensity Levels:
- High: The trait is very noticeable. It is expressed often and in a detailed manner.
- Medium: The trait is somewhat noticeable, but the expressions of it are limited.
- Low: The trait is barely noticeable, with very few indications of its presence.
- None: There is no indication of the trait at all; it is completely absent.

Content Consideration:
- Focus on searches that demonstrate planning, organization, and diligence for assessing Openness and Conscientiousness. \
- Avoid assuming a base level of these traits due to the nature of the data (search histories).

Text: <<< {text} >>>

Trait Positive and Negative Marker Indicators: {markers}

Output Format: format your response as a JSON object, using the trait names as keys and the assigned levels as values.

Expected JSON Output Format:
{{
    "openness": "[level]",
    "conscientiousness": "[level]",
    "extraversion": "[level]",
    "agreeableness": "[level]",
    "neuroticism": "[level]"
}}

- Replace "[level]" with the appropriate level (High, Medium, Low, None) based on your analysis.
- Ensure that the response strictly adheres to the JSON format specified.

Perform the Task. Begin by thinking step by step and following the described Task Procedure to accomplish the Objetive. Explain
you answer, specifially the rationale behind the assigned trait levels, with an in-depth explanation of why a specific level was assigned to each trait.
Elaborate on the particular elements in the Text for Analysis that influenced the decision for each trait level, clarifying the reasoning and \
thought process behind these classifications.
"""

CLASSIFICATION_TEMPLATE_CONV = """
Role: Psychologist specializing in OCEAN personality traits.

Task: Analyze the personality traits of 'user' in a series of chat conversations. These \
conversations are concatenated and enclosed within <<< >>> markers.

Text for Analysis:
- Concentrate on the complete text set within <<< >>> markers, which consists of concatenated \
chat logs between 'user' and various individuals.

Objective:
- Evaluate the 'user's levels of Openness, Conscientiousness, Extraversion, Agreeableness, and \
Neuroticism based on their expressions in these chat logs.

Task Procedure:
1. Review the entire set of chat logs within <<< >>> markers, focusing on messages sent by 'user'.
3. Assess the intensity of each OCEAN trait in 'user's expressions based on frequency and depth.

Intensity Levels:
- High: The trait is very noticeable. It is expressed often and in a detailed manner.
- Medium: The trait is somewhat noticeable, but the expressions of it are limited.
- Low: The trait is barely noticeable, with very few indications of its presence.
- None: There is no indication of the trait at all; it is completely absent.

Text: <<< {text} >>>

Trait Markers: {markers}

Output Format: format your response as a JSON object, using the trait names as keys and the assigned levels as values.

Expected JSON Output Format:
{{
    "openness": "[level]",
    "conscientiousness": "[level]",
    "extraversion": "[level]",
    "agreeableness": "[level]",
    "neuroticism": "[level]"
}}

- Replace "[level]" with the appropriate level (high, medium, low, none) based on your analysis.
- Ensure that the response strictly adheres to the JSON format specified.

Perform the Task. Begin by thinking step by step and following the described Task Procedure to accomplish the Objetive. Explain
you answer, specifially the rationale behind the assigned trait levels, with an in-depth explanation of why a specific level was assigned to each trait.
Elaborate on the particular elements in the Text for Analysis that influenced the decision for each trait level, clarifying the reasoning and \
thought process behind these classifications.
"""
