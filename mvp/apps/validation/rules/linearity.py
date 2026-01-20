from apps.stats.calculations import linear_regression


def evaluate_linearity(concentrations, responses):
    """
    Evaluate linearity according to ICH Q2(R1) guidelines.

    Acceptance criteria:
    - Correlation coefficient (r) >= 0.99
    - y-intercept should not differ significantly from zero

    Returns: dict with status, metrics, justification
    """
    try:
        slope, intercept, r_squared = linear_regression(concentrations, responses)

        # ICH Q2: correlation coefficient >= 0.99
        passed = r_squared >= 0.99

        # Additional check: y-intercept should be within reasonable range
        # For simplicity, accept if |intercept| < 10% of max response
        max_response = max(responses)
        intercept_ok = abs(intercept) < 0.1 * max_response

        passed = passed and intercept_ok

        justification = []
        if r_squared >= 0.99:
            justification.append(f"Correlation coefficient (r² = {r_squared:.4f}) meets requirement (>=0.99)")
        else:
            justification.append(f"Correlation coefficient (r² = {r_squared:.4f}) does not meet requirement (>=0.99)")

        if intercept_ok:
            justification.append(f"Y-intercept ({intercept:.4f}) is acceptable")
        else:
            justification.append(f"Y-intercept ({intercept:.4f}) is too high")

        return {
            'status': 'PASS' if passed else 'FAIL',
            'metrics': {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_squared,
            },
            'justification': '; '.join(justification)
        }
    except Exception as e:
        return {
            'status': 'FAIL',
            'metrics': {},
            'justification': f'Error in calculation: {str(e)}'
        }
