# FirScript

![PyPI](https://img.shields.io/pypi/v/firscript)
![License](https://img.shields.io/github/license/JungleDome/FirScript)

**A modular scripting engine designed for algo trading.**
Write PineScript-like python code to define strategies, indicators, and libraries — then plug them into a clean, scriptable engine that does the orchestration for you.

---

## 💡 Why FirScript?

Building your own backtesting stack?  
FirScript gives you a flexible core to run strategy and indicator code, manage dependencies, and control execution — without locking you into one opinionated interface.

- ✅ Write strategy logic as regular Python scripts
- ⚙️ Parse, register, and run strategies dynamically
- 🧹 Bring your own data, namespaces, and post-processors
- 🛠️ Easily embed into larger trading and backtesting systems or apps
- 🧪 Perfect for research, prototyping, and integration into custom trading platforms

---

## Table of Contents

- [Getting Started](#getting-started)
- [Namespaces, Your Way](#namespaces-your-way)
- [Who is FirScript for?](#who-is-firscript-for)
- [What FirScript Isn't](#what-firscript-isnt)
- [Contribute](#contribute)
- [License](#license)

---
## Getting Started

### 📦 Installation

```bash
pip install FirScript
```

### 🚀 Quick Start

```python
from FirScript import Engine

strategy_source = '''
def setup():
    global fast_length, slow_length
    fast_length = input.int("Fast MA Length", 10)
    slow_length = input.int("Slow MA Length", 20)

def process():
    if ta.crossover(ta.ema(data.all.close, fast_length), ta.ema(data.all.close, slow_length)):
        strategy.long()
'''

data = pd.DataFrame({
        'timestamp': pd.date_range('2025-01-01', periods=50),
        'open': [100 + 0.5*i + random.random() for i in range(50)],
        'close': [100 + 0.5*i + random.random() for i in range(50)],
        'high': [100 + 0.5*i + random.random() for i in range(50)],
        'low': [100 + 0.5*i + random.random() for i in range(50)],
        'volume': [100 + 0.5*i + random.random() for i in range(50)]
    })

engine = Engine(data, main_script_str=strategy_source)
results = engine.run()

print(results)
```

TADA - You just ran your first strategy!

---

### 💡 Examples

Want to see it in action? Explore these ready-to-run examples in the [examples](https://github.com/JungleDome/FirScript/tree/main/examples) folder:

- [Simple Strategy](examples/simple_strategy.py) – A basic trading strategy to get you started.
- [Simple Indicator](examples/simple_indicator.py) – How to define and use a custom indicator.
- [Simple Library](examples/simple_library.py) – Create reusable components with a simple library.
- [Importing Indicators Into Strategy](examples/strategy_with_indicator_import.py) – Combine indicators into your strategy logic.
- [Using Libraries In Strategy](examples/strategy_with_library_import.py) – Integrate libraries directly into your strategies.
- [Custom Namespace](examples/custom_namespace.py) – Extend your functionality using custom namespaces.

---

## 🧠 Namespaces, Your Way

FirScript ships with default namespaces (`ta`, `input`, `chart`, `color`, `data`, `strategy`) — but you can register your own.

```python
class MySignals:
    @staticmethod
    def crossover(fast, slow):
        return (fast > slow) & (fast.shift() < slow.shift())

registry.register("signals", MySignals())
```

Now your script can do:

```python
if signals.crossover(ema_fast, ema_slow):
    strategy.long()
```

Check out the [full implementation](examples/custom_namespace.py) here.

---

## 🧹 Who is FirScript for?

- Build your own backtesting UI or cloud platform
- Dynamically load and run user-submitted strategies
- Combine with Pandas, Plotly, or any data science tool
- Use as a logic core for live or paper trading systems

---

## 🚫 What FirScript Isn't
- ❌ A charting library (use Plotly, Matplotlib, etc.)
- ❌ A full broker API or execution engine
- ❌ A replacement for full frameworks like Backtrader — FirScript is lean, modular, and pluggable

---

## 🤝 Contribute

We welcome issues, ideas, and PRs — especially if you're building on top of this engine.

[Contributing Guide](CONTRIBUTING.md)


## 📖 License

FirScript is licensed under a [MIT license](https://github.com/JungleDome/FirScript/blob/main/LICENSE).
