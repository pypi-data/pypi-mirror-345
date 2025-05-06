import z3scn as dev
import time
import math

def z3setup(**kwargs) -> list[int]:
    """
    Prepare ordered and validated actuator initialization parameters.

    Parameters (all optional except 'com'):
        com (int): Required. COM port number (e.g., 4 for COM4).
        id (int): Device ID (default 0).
        stroke (int): Stroke length (default 100, only 50, 150, or 200 are valid; others become 100).
        accel (int): Acceleration value (default 200).
        gain (int): Control gain (default 7).
        normalSpd (int): Normal movement speed (default 7800).
        homeSpd (int): Homing speed (default 2000, change this value with TBVST or CAT app).
        moveMode (int): Movement mode (default 0).
        gohome (int): Whether to go home on init (default 0).
        gocenter (int): Whether to go center after home (default 0).
        diag (int): Diagnostic flag (default 0).

    Returns:
        list[int]: A list of parameters ready to be unpacked into the init() function.

    Raises:
        ValueError: If 'com' is missing or unknown parameters are passed.

    Example:
        params = z3setup(com=4, accel=385, normalSpd=10000 )
        dev.init(*params)
    """
    param_order = ["com", "id", "stroke", "accel", "gain", "normalSpd", "homeSpd", "moveMode", "gohome", "gocenter", "diag"]
    defaults = {
        "id": 0, "stroke": 100, "accel": 200, "gain": 7,
        "normalSpd": 7800, "homeSpd": 2000, "moveMode": 0,
        "gohome": 0, "gocenter": 0, "diag": 0
    }
    stroke_valid = {50, 150, 200}

    allowed_keys = set(param_order)
    for key in kwargs:
        if key not in allowed_keys:
            raise ValueError(f"Unknown parameter '{key}'. Allowed parameters are: {', '.join(param_order)}")

    if "com" not in kwargs:
        raise ValueError("Parameter 'com' is required")

    stroke = kwargs.get("stroke", 100)
    kwargs["stroke"] = stroke if stroke in stroke_valid else 100

    args = [kwargs.get(k, defaults.get(k)) for k in param_order]

    while len(args) > 1 and args[-1] == defaults.get(param_order[len(args)-1]):
        args.pop()

    # print(f"[DEBUG] Prepared args: {args}")
    return args


# smooth filter
def smooth_path(start, end, steps):
    return [round(start + (end - start) * 0.5 * (1 - math.cos(math.pi * i / steps)), 2)
            for i in range(steps + 1)]

def sleep(ms):
    time.sleep(ms / 1000.0)

def frange(start, stop, step):
    while start < stop:
        yield start
        start += step

# init scn with COM Port 4 and default parameters (stroke = 100)
if dev.init(*z3setup(com=4)):
    print("Start Testing...")

    z3vers = dev.get_device_info("version")
    print(f"Version: {z3vers}")
    z3name = dev.get_device_info("name")
    print(f"Name: {z3name}\n")
    z3tks = dev.get_device_info("ticks")
    print(f"Ticks: {z3tks}\n")
    z3type = dev.get_device_info("type")
    print(f"type: {z3type}\n")

    z3vid = dev.get_device_info("vendor id")
    print(f"VID: {z3vid}\n")
    z3pid = dev.get_device_info("product id")
    print(f"PID: {z3pid}\n")

    # SCN actuator 100mm
    max_stroke = 100
    pos_center = max_stroke / 2

    # go home position
    dev.go_home()
    dev.submit_check()
    sleep(100)

    # go center position
    if dev.go_center():
        dev.submit_check()
        sleep(100)
    else:
        print("error center failed!") 

    # Params
    pause_fast = 0.05  # quick pause between small move
    pause_long = 0.1   # long pause 500 ms
    repetitions = 2   # cycles

    # key pos.
    low_rest = 20
    low_min = 20
    low_max = 40

    high_rest = 70
    high_min = 70
    high_max = 90

    for cycle in range(repetitions):
            print(f"\n--- Cycle {cycle+1} ---")

            # 1. start Position
            dev.load_position(low_rest)
            dev.submit_check()
            sleep(100)

            # 2. fast move low position
            for _ in range(5):
                for move in (low_max, low_min):
                    dev.go_position(move)
                    time.sleep(pause_fast)

            # 3. Pause
            dev.load_position(high_rest)
            dev.submit_check()
            sleep(500)

            # 4. fast move high position
            for _ in range(5):
                for move in (high_max, high_min):
                    dev.go_position(move)
                    time.sleep(pause_fast)

            # 5. return and pause
            dev.load_position(low_rest)
            dev.submit_check()
            sleep(500)

    # return to center position
    dev.go_center()
    dev.submit_check()
    sleep(100)

    # notify device extension
    dev.terminate()

    print("Test Done!")
else:
    print("Initialization failed!")