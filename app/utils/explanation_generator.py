"""
explanation_generator.py
--------------------------
Generates a human-readable, AI-style explanation for why a job
posting was classified as FAKE or GENUINE.

This module combines:
    1. The ML model's prediction probability
    2. The rule-based red flags detected

to build a natural language explanation, without requiring an
external paid AI API (works fully offline / template-based).

If you want to use a real generative AI API (e.g., OpenAI/Anthropic),
you can replace `generate_explanation()` with an API call that sends
the job details + red flags as a prompt and returns the response text.
"""


def generate_explanation(prediction, scam_probability, red_flag_result, job_title):
    """
    Build a natural-language explanation for the classification result.

    Parameters
    ----------
    prediction : int
        0 = Genuine, 1 = Fake
    scam_probability : float
        Probability (0-100) that the job is fake
    red_flag_result : dict
        Output of analyze_red_flags() containing 'flags' and 'flag_count'
    job_title : str
        Title of the job posting

    Returns
    -------
    str : explanation text
    """
    detected_flags = [f["name"] for f in red_flag_result["flags"] if f["detected"]]
    flag_count = red_flag_result["flag_count"]

    if prediction == 1:
        # FAKE job explanation
        intro = (
            f"Based on our analysis, the job posting \"{job_title}\" has been "
            f"classified as a LIKELY FAKE/SCAM job posting with a scam "
            f"probability of {scam_probability}%."
        )

        if flag_count > 0:
            flag_text = (
                f"This decision was strongly influenced by {flag_count} red flag(s) "
                f"detected in the posting: {', '.join(detected_flags)}. "
            )
            details = []
            for f in red_flag_result["flags"]:
                if f["detected"]:
                    details.append(f"- {f['name']}: {f['description']}")
            reason_block = "\n".join(details)
            explanation = (
                f"{intro}\n\n{flag_text}\n\n"
                f"Specific concerns:\n{reason_block}\n\n"
                f"Recommendation: Exercise extreme caution. Do NOT pay any money, "
                f"share bank details, Aadhar/PAN, or other sensitive personal "
                f"information for this job. Verify the company independently "
                f"through its official website and registered contact channels "
                f"before proceeding."
            )
        else:
            explanation = (
                f"{intro}\n\nWhile no obvious red flags were detected in the "
                f"structured fields, the language patterns and overall content "
                f"of the posting closely match patterns commonly seen in "
                f"fraudulent job advertisements based on our trained model.\n\n"
                f"Recommendation: Proceed with caution and verify the employer "
                f"independently before sharing any personal information."
            )

    else:
        # GENUINE job explanation
        intro = (
            f"Based on our analysis, the job posting \"{job_title}\" appears to "
            f"be a GENUINE job posting, with a scam probability of only "
            f"{scam_probability}%."
        )

        if flag_count == 0:
            explanation = (
                f"{intro}\n\nNo red flags were detected. The posting includes "
                f"reasonable company details, a realistic salary range, and "
                f"professional language consistent with legitimate job "
                f"advertisements.\n\n"
                f"Recommendation: This posting looks safe, but it is always a "
                f"good practice to verify the company's official website and "
                f"reviews before applying."
            )
        else:
            flag_text = ", ".join(detected_flags)
            explanation = (
                f"{intro}\n\nHowever, {flag_count} minor red flag(s) were noted: "
                f"{flag_text}. These did not significantly affect the overall "
                f"classification, but it is recommended to review these points "
                f"carefully.\n\n"
                f"Recommendation: This posting is likely genuine, but verify "
                f"the highlighted points before proceeding."
            )

    return explanation
