from intent_envelope import IntentEnvelope
from decay_tracker import IntentDecayTracker

def run_demo():
    tracker = IntentDecayTracker()

    print("\n══════════════════════════════════════════")
    print("  INTENT HANDOFF PROTOTYPE — DEMO")
    print("══════════════════════════════════════════")

    # Create the initial intent envelope
    envelope = IntentEnvelope(
        task="find the cheapest gas route for swapping $50M USDT to AAVE",
        why="user wants to minimize cost, not speed — large institutional order",
        constraints=["max slippage 0.5%", "deadline in 10 mins", "no single-hop AMM"],
        attempted=[],
        confidence=0.92,
        origin_agent="RootAgent",
        current_agent="RootAgent"
    )

    print(f"\n[ORIGIN] {envelope.origin_agent} created intent envelope")
    print(envelope.summary())

    # Hop 1 — RootAgent → PricingAgent
    print(f"\n[HOP 1] Transferring to PricingAgent...")
    envelope.transfer_to("PricingAgent", note="needs live token prices before routing")
    envelope.attempted.append("fetched USDT price: $1.00, AAVE price: $112.76")
    result = tracker.evaluate(envelope)
    tracker.report(result)
    print(envelope.summary())

    # Hop 2 — PricingAgent → LiquidityAgent
    print(f"\n[HOP 2] Transferring to LiquidityAgent...")
    envelope.transfer_to("LiquidityAgent", note="prices fetched, now check pool depth")
    envelope.attempted.append("checked WETH/AAVE pool — depth $8M, order is 630% of depth")
    result = tracker.evaluate(envelope)
    tracker.report(result)
    print(envelope.summary())

    # Hop 3 — LiquidityAgent → ClassifierAgent
    print(f"\n[HOP 3] Transferring to ClassifierAgent...")
    envelope.transfer_to("ClassifierAgent", note="liquidity checked, classify the order")
    envelope.attempted.append("classified as TIER 3 — single swap blocked, TWAP required")
    result = tracker.evaluate(envelope)
    tracker.report(result)
    print(envelope.summary())

    # Hop 4 — ClassifierAgent → ExecutionAgent
    print(f"\n[HOP 4] Transferring to ExecutionAgent...")
    envelope.transfer_to("ExecutionAgent", note="classification done, plan execution")
    envelope.attempted.append("planned 26 tranches over 5 hours via Uniswap V3")
    result = tracker.evaluate(envelope)
    tracker.report(result)
    print(envelope.summary())

    # Hop 5 — ExecutionAgent → VerificationAgent (this is where decay kills it)
    print(f"\n[HOP 5] Transferring to VerificationAgent...")
    envelope.transfer_to("VerificationAgent", note="execution planned, verify before submit")
    result = tracker.evaluate(envelope)
    tracker.report(result)
    print(envelope.summary())

    print("\n══════════════════════════════════════════")
    print("  FINAL DECISION")
    print("══════════════════════════════════════════")
    print(f"  Action: {result['action'].upper()}")
    if result['action'] in ['route_to_human', 'abort_and_escalate']:
        print(f"  Reason: Intent confidence too degraded after {result['hops']} hops")
        print(f"  Original intent: {envelope.why}")
        print(f"  Re-anchor required before execution proceeds")
    print("══════════════════════════════════════════\n")

if __name__ == "__main__":
    run_demo()