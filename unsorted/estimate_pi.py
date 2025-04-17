import time, random
def estimate_pi(
    n_points: int,
    show_estimate: bool,
) -> None:
    """
    Simple Monte Carlo Pi estimation calculation.
    Parameters
    ----------
    n_points
        number of random numbers used to for estimation.
    show_estimate
        if True, will show the estimation of Pi, otherwise
        will not output anything.
    """
    within_circle = 0

    for _ in range(n_points):
        x, y = (random.uniform(-1, 1) for v in range(2))
        radius_squared = x**2 + y**2

        if radius_squared <= 1:
            within_circle += 1

    pi_estimate = 4 * within_circle / n_points

    if not show_estimate:
        print("Final Estimation of Pi=", pi_estimate)


def run_test(
    n_points: int,
    n_repeats: int,
    only_time: bool,
) -> None:
    """
    Perform the tests and measure required time.
    Parameters
    ----------
    n_points
        number of random numbers used to for estimation.
    n_repeats
        number of times the test is repeated.
    only_time
        if True will only print the time, otherwise
        will also show the Pi estimate and a neat formatted
        time.
    """
    start_time = time.time()

    for _ in range(n_repeats):
        estimate_pi(n_points, only_time)

    if only_time:
        print(f"{(time.time() - start_time)/n_repeats:.4f}")
    else:
        print(
            f"Estimating pi took {(time.time() - start_time)/n_repeats:.4f} seconds per run."
        )

run_test(10000000, 10,False)