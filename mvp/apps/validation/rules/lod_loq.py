from apps.stats.calculations import calculate_lod_lod


def evaluate_lod_loq(blank_responses, slope):
    """
    Evaluate LOD and LOQ according to ICH Q2(R1) guidelines.

    LOD = 3.3 * σ / S
    LOQ = 10 * σ / S

    Where σ is standard deviation of blank responses, S is slope from linearity.

    Acceptance criteria: LOD and LOQ should be reasonable (no specific limits in ICH Q2,
    but typically LOD should be < LOQ, and both should be quantifiable).

    For MVP, we just calculate and assume pass if calculated successfully.

    Returns: dict with status, metrics, justification
    """
    try:
        lod, loq = calculate_lod_lod(blank_responses, slope)

        # Basic validation
        passed = lod > 0 and loq > 0 and lod < loq

        justification = []
        if passed:
            justification.append(f"LOD ({lod:.4f}) and LOQ ({loq:.4f}) calculated successfully")
        else:
            justification.append("LOD/LOQ calculation failed or invalid values")

        return {
            'status': 'PASS' if passed else 'FAIL',
            'metrics': {
                'lod': lod,
                'loq': loq,
            },
            'justification': '; '.join(justification)
        }
    except Exception as e:
        return {
            'status': 'FAIL',
            'metrics': {},
            'justification': f'Error in calculation: {str(e)}'
        }
