from apps.stats.calculations import calculate_recovery, calculate_rsd
import statistics


def evaluate_accuracy(level, measured_values):
    """
    Evaluate accuracy according to ICH Q2(R1) guidelines.

    Acceptance criteria for recovery:
    - 80-120% recovery
    - %RSD <= 2.0% for n>=6, <=5.0% for n=3-5

    Returns: dict with status, metrics, justification
    """
    try:
        recoveries = [calculate_recovery(float(level)/100 * 100, m) for m in measured_values]  # assuming nominal 100
        mean_recovery = statistics.mean(recoveries)
        rsd = calculate_rsd(recoveries)

        # ICH Q2 accuracy criteria
        recovery_ok = 80 <= mean_recovery <= 120

        # RSD criteria
        n = len(measured_values)
        if n >= 6:
            rsd_limit = 2.0
        elif n >= 3:
            rsd_limit = 5.0
        else:
            rsd_limit = 10.0  # conservative

        rsd_ok = rsd <= rsd_limit

        passed = recovery_ok and rsd_ok

        justification = []
        if recovery_ok:
            justification.append(f"Mean recovery ({mean_recovery:.2f}%) is within 80-120%")
        else:
            justification.append(f"Mean recovery ({mean_recovery:.2f}%) is outside 80-120%")

        if rsd_ok:
            justification.append(f"%RSD ({rsd:.2f}%) meets requirement (<= {rsd_limit:.1f}%)")
        else:
            justification.append(f"%RSD ({rsd:.2f}%) does not meet requirement (<= {rsd_limit:.1f}%)")

        return {
            'status': 'PASS' if passed else 'FAIL',
            'metrics': {
                'recoveries': recoveries,
                'mean_recovery': mean_recovery,
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
