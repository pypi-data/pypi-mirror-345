"""
Command line interface for the eye2color package.
"""
import argparse
import json
import logging
import numpy as np
from datetime import datetime
from .math_utils import compute_XZ, compute_uv_prime
from .device import Eye2CLI


def main():
    parser = argparse.ArgumentParser(description='EYE2-400 MES,1 Simple CLI')
    parser.add_argument('--port', required=True, help='Serial port (e.g., COM3)')
    parser.add_argument('--timeout', type=float, default=2.0, help='Read timeout (s)')
    parser.add_argument('--eol', choices=['CR', 'LF', 'CRLF'], default='CR')
    parser.add_argument('--output', help='Output CSV file path')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv', help='Output format')
    parser.add_argument('--verbose', '-v', action='count', default=0, help='Increase verbosity')
    args = parser.parse_args()
    
    # Logging setup
    log_level = logging.WARNING
    if args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose >= 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    
    # Determine output filename
    if not args.output:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f'measurement_{timestamp}.csv'

    cli = Eye2CLI(args.port, timeout=args.timeout, eol=args.eol)
    result = cli.measure()
    cli.close()

    # Basic measurements
    x = float(result['x'])
    y = float(result['y'])
    Lv = float(result['Lv'])

    # Derived
    X, Z = compute_XZ(x, y, Lv)
    u_prime, v_prime = compute_uv_prime(X, Lv, Z)
    n = (x - 0.3320) / (y - 0.1858)
    cct = -449 * n**3 + 3525 * n**2 - 6823.3 * n + 5520.33

    # duv
    if cct <= 7000:
        k0, k1, k2, k3 = -0.24748, 0.09091, 0.00004, -0.00004
    else:
        k0, k1, k2, k3 = -0.17858, 0.07145, 0.00008, -0.00006
    v_planck = k0 + k1 * u_prime + k2 * cct + k3 * u_prime * cct
    duv = v_prime - v_planck

    # Dominant wavelength & purity
    x_w, y_w = 0.3127, 0.3290
    dist_to_white = np.hypot(x - x_w, y - y_w)
    theta = np.arctan2(y - y_w, x - x_w)
    dw = 380 + 400 * (theta + np.pi) / (2 * np.pi)
    pe = dist_to_white / 0.5

    # Format output
    row = {
        'X': f"{X:.6f}",
        'Y': f"{Lv:.6f}",
        'Z': f"{Z:.6f}",
        'x': f"{x:.7f}",
        'y': f"{y:.7f}",
        'Lv': f"{Lv:.6f}",
        "u'": f"{u_prime:.6f}",
        "v'": f"{v_prime:.6f}",
        'Tcp': f"{cct:.0f}",
        'duv': f"{duv:.6f}",
        'λd': f"{dw:.2f}",
        'Pe': f"{pe * 100:.2f}"
    }

    headers = ['X', 'Y', 'Z', 'x', 'y', 'Lv', "u'", "v'", 'Tcp', 'duv', 'λd', 'Pe']
    header_line = ','.join(headers)
    value_line = ','.join(row[h] for h in headers)

    json_data = {}
    for key, value in row.items():
        try:
            json_data[key] = float(value) if '.' in value else int(value)
        except ValueError:
            json_data[key] = value

    if args.format == 'json':
        print(json.dumps(json_data))
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(header_line + '\n')
            f.write(value_line + '\n')
        logging.info(f"Data saved to {args.output}")
        print(header_line)
        print(value_line)
