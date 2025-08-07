# Project Plan

## Goal
Build a fully autonomous, robust crypto futures trading bot that turns starting capital into sustained PnL.

---

## Current Phase
**Phase 2: Strategy Framework**  
- Completed: Phase 1 (Data infra, ETL, backfill, caching/rate-limits).  
- Up next: 2.1–2.2 (BaseStrategy + ExampleMomentum)  

---

## Next GPT Prompt
When back at your desk, paste this into ChatGPT to auto-generate Sprint 2 files:

> **System**: You are a world-class quantitative developer.  
>  
> **Task**: Implement **Phase 2.1–2.2**:  
> 1. `src/strategy/base_strategy.py` with abstract `generate_signals(df)` contract.  
> 2. `src/strategy/example_momentum.py` implementing a 20/50 EMA crossover strategy, outputting signals as `{"timestamp","side","size"}`.  
> 3. Unit tests:  
>    - `tests/test_base_strategy.py` ensures that `BaseStrategy` raises `NotImplementedError`.  
>    - `tests/test_example_momentum.py` uses a small DataFrame to verify buy/sell signals at correct crossover points.  
>  
> **Constraints**:  
> - Use Pandas.  
> - Signals must use UTC timestamps.  
> - Code must be paste-ready, include type hints and docstrings.  
>  
> **Deliverables**:  
> - `src/strategy/base_strategy.py`  
> - `src/strategy/example_momentum.py`  
> - `tests/test_base_strategy.py`  
> - `tests/test_example_momentum.py`

---

## Roadmap Snapshot
- **0** Governance & Resilience ✅  
- **1** Data Infra & ETL ✅  
- **1.3** Caching & Rate-Limits ✅  
- **2** Strategy Framework ⏳  
- **3** Backtesting & Simulation  
- … through Phase 10

---

### How to use
- Keep updating **`PROJECT.md`** after each sprint: mark it complete, bump “Current Phase,” and paste the next prompt.  
- At the start of any ChatGPT session, copy-paste the contents of `PROJECT.md` so the model has full context.

---

