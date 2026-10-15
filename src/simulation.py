"""Daily inventory simulation for ONE store-item: continuous review, (s, Q) policy."""
import math

import numpy as np


def simulate_series(demand, weekly_fc, safety_stock, q, lead, unit_cost, unit_price,
                    hold_rate, order_cost, penalty_mult):
    n, lead = len(demand), int(lead)
    arrivals = np.zeros(n + lead + 1)      # arrivals[d] = units landing at the start of day d
    on_hand, on_order = float(q), 0.0      # same start for every policy: one EOQ in stock
    unmet = inv_sum = 0.0
    stockout_days = n_orders = 0

    for d in range(n):
        on_hand += arrivals[d]                         # 1. receive deliveries
        on_order -= arrivals[d]
        sold = min(on_hand, demand[d])                 # 2. serve demand, shortfall is lost
        if sold < demand[d]:
            stockout_days += 1
            unmet += demand[d] - sold
        on_hand -= sold

        # 3. reorder point for THIS week, from information known at the start of the week
        s = weekly_fc[d // 7] / 7 * lead + safety_stock
        position = on_hand + on_order
        if position <= s:
            qty = max(1, math.ceil((s - position) / q)) * q   # whole EOQ multiples
            arrivals[d + lead] += qty
            on_order += qty
            n_orders += 1
        inv_sum += on_hand                             # end-of-day stock

    total = float(np.sum(demand))
    hold = inv_sum / n * unit_cost * hold_rate * n / 365
    ordering = n_orders * order_cost
    stockout = unmet * (unit_price - unit_cost) * penalty_mult
    return dict(service_level=1 - unmet / total, stockouts=stockout_days,
                avg_inventory=inv_sum / n, demand_units=total, unmet_units=unmet,
                holding_cost=hold, ordering_cost=ordering, stockout_cost=stockout,
                total_cost=hold + ordering + stockout)