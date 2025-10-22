"""
This file contains all core mathematical functions for
weight and balance calculations.
"""
import src.config as config

def interpolate_arm(arm_table, fill_l):
    """
    Linearly interpolates an arm value from a given table.

    The table is expected to be a list of [liters, arm] pairs,
    sorted by liters.

    Args:
        arm_table (list[list[float]]): The lookup table of [liters, arm] points.
        fill_l (float): The current fill level in liters to find the arm for.

    Returns:
        float: The interpolated arm in inches. Returns boundary values
               if fill_l is outside the table's range.
    """
    # Handle edge cases: below or at the first point
    if fill_l <= arm_table[0][0]:
        return arm_table[0][1]

    # Handle edge cases: above or at the last point
    if fill_l >= arm_table[-1][0]:
        return arm_table[-1][1]

    # Find the two points to interpolate between
    for i in range(1, len(arm_table)):
        if fill_l < arm_table[i][0]:
            l1, a1 = arm_table[i - 1]
            l2, a2 = arm_table[i]

            # Perform linear interpolation
            if (l2 - l1) == 0:  # Avoid division by zero
                return a1
            percentage = (fill_l - l1) / (l2 - l1)
            return a1 + (a2 - a1) * percentage

    # As a fallback, return the last arm
    return arm_table[-1][1]


def klm_index(weight_kg, arm_in, reference_arm_in=config.KLM_REFERENCE_ARM_IN,
              scale=config.KLM_SCALE, offset=config.KLM_OFFSET):
    """
    Calculates the KLM-style Load Index (CGI).

    Args:
        weight_kg (float): The weight of the item in kilograms.
        arm_in (float): The arm (distance from datum) in inches.
        reference_arm_in (float, optional): The reference arm defined by the
                                            index system. Defaults to config.
        scale (int, optional): The scaling factor for the index. Defaults to config.
        offset (int, optional): The offset for the index. Defaults to config.

    Returns:
        float: The calculated index. Returns 0 if weight is 0.
    """
    if weight_kg == 0:
        return 0
    return (weight_kg * (arm_in - reference_arm_in)) / scale + offset


def calculate_arm_from_doi(doi, weight_kg, reference_arm_in=config.KLM_REFERENCE_ARM_IN,
                           scale=config.KLM_SCALE, offset=config.KLM_OFFSET):
    """
    Reverse-calculates the arm in inches from a given DOI (DOW Index).

    Args:
        doi (float): The Dry Operating Index.
        weight_kg (float): The Dry Operating Weight in kilograms.
        reference_arm_in (float, optional): The reference arm. Defaults to config.
        scale (int, optional): The scaling factor. Defaults to config.
        offset (int, optional): The offset. Defaults to config.

    Returns:
        float: The calculated arm in inches.
    """
    if weight_kg == 0:
        return 0
    # Formula: DOI = (weight * (arm - ref_arm)) / scale + offset
    # Solved for arm: arm = ((DOI - offset) * scale / weight) + ref_arm
    return ((doi - offset) * scale / weight_kg) + reference_arm_in


def calculate_mac_percent(arm_in, le_mac_in=config.LE_MAC_IN, mac_length_in=config.MAC_LENGTH_IN):
    """
    Calculates the Center of Gravity as a percentage of Mean Aerodynamic Chord (%MAC).

    Args:
        arm_in (float): The arm (distance from datum) in inches.
        le_mac_in (float, optional): The leading edge of MAC in inches. Defaults to config.
        mac_length_in (float, optional): The length of MAC in inches. Defaults to config.

    Returns:
        float: The CG position in %MAC.
    """
    if mac_length_in == 0:
        return 0
    return ((arm_in - le_mac_in) * 100 / mac_length_in)


def check_limits(zfw_weight, tow_weight, limits):
    """
    Checks ZFW and TOW against the aircraft's certified weight limits.

    Args:
        zfw_weight (float): The calculated Zero Fuel Weight.
        tow_weight (float): The calculated Takeoff Weight.
        limits (dict): A dictionary containing limit keys
                       ("MZFW_kg", "MTOW_kg", "MTW_kg", "MFW_kg").

    Returns:
        list[str]: A list of warning messages. Empty if all limits are respected.
    """
    messages = []
    if zfw_weight > limits["MZFW_kg"]:
        over = zfw_weight - limits["MZFW_kg"]
        messages.append(
            f"Zero Fuel Weight ({zfw_weight:.1f} kg) exceeds Maximum ZFW ({limits['MZFW_kg']} kg) by {over:.1f} kg.")
    if tow_weight > limits["MTOW_kg"]:
        over = tow_weight - limits["MTOW_kg"]
        messages.append(
            f"Takeoff Weight ({tow_weight:.1f} kg) exceeds Maximum TOW ({limits['MTOW_kg']} kg) by {over:.1f} kg.")
    if tow_weight > limits["MTW_kg"]:
        over = tow_weight - limits["MTW_kg"]
        messages.append(
            f"Takeof Weight ({tow_weight:.1f} kg) exceeds Maximum Taxi Weight ({limits['MTW_kg']} kg) by {over:.1f} kg.")
    # Note: MFW is likely Minimum Flight Weight, which ZFW should be above
    if zfw_weight < limits["MFW_kg"]:
        under = limits["MFW_kg"] - zfw_weight
        messages.append(
            f"Zero Fuel Weight ({zfw_weight:.1f} kg) is below Minimum Flight Weight ({limits['MFW_kg']} kg) by {under:.1f} kg.")
    return messages