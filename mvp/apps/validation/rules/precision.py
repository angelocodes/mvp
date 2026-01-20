from apps.stats.calculations import calculate_rsd
import statistics


def evaluate_precision(replicate_values):
    """
    Evaluate precision (repeatability) according to ICH Q2(R1) guidelines.

    Acceptance criteria:
    - %RSD <= 2.0% for n>=6, <=5.0% for n=3-5

    Returns: dict with status, metrics, justification
    """
    try:
        mean_val = statistics.mean(replicate_values)
        rsd = calculate_rsd(replicate_values)

        # ICH Q2 precision criteria
        n = len(replicate_values)
        if n >= 6:
            rsd_limit = 2.0
        elif n >= 3:
            rsd_limit = 5.0
        else:
            rsd_limit = 10.0  # conservative

        passed = rsd <= rsd_limit

        justification = []
        if passed:
            justification.append(f"%RSD ({rsd:.2f}%) meets requirement (<= {rsd_limit:.1f}%)")
        else:
            justification.append(f"%RSD ({rsd:.2f}%) does not meet requirement (<= {rsd_limit:.1f}%)")

        return {
            'status': 'PASS' if passed else 'FAIL',
            'metrics': {
                'mean': mean_val,
                'rsd': rsd,
            },
            'justification': '; '.join(justification)
        }
    except Exception as e:
        return {
            'status': 'FAIL',
            'metrics': {},
            'justification': f'Error in calculation: {str(e)}'
        }
