"""Battery-level helpers shared by Photon and its host-side tests."""


def percentage_from_voltage(voltage, empty_voltage=2.8, full_voltage=4.2):
    percentage = round(
        100 * (voltage - empty_voltage) / (full_voltage - empty_voltage)
    )
    return max(0, min(100, percentage))
