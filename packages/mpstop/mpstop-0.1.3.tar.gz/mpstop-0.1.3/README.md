# mpstop

*Pronounced "em-pee-ess-top" (like 'MPS' + 'top')*

**mpstop** is a minimal, fast, and user-friendly system monitor for Apple Silicon (M1/M2/M3) Macs. Inspired by `htop` and `nvitop`, `mpstop` gives you a real-time, terminal-based view of your Mac's GPU (MPS), CPU, memory, and Python process usage. Perfect for developers, researchers, and anyone who wants to keep an eye on their Mac's performance.

---

## Features
- Live Apple Silicon GPU (MPS) core utilization
- System memory and CPU usage
- Active Python processes (user, memory %, CPU %, time, command)
- Clean, minimal terminal interface

---

## Installation

**Option 1: From PyPI**
```sh
pip install mpstop
```

**Option 2: From source**
```sh
git clone https://github.com/gokulkarthik/mpstop
cd mpstop
pip install .
```

---

## How to Launch

After installation, simply run:

```sh
mpstop
```

Or, if you prefer to run directly from the source:

```sh
python -m mpstop
```

---

## Screenshot

Below is a sample screenshot of mpstop in action:

![mpstop demo screenshot](demo.png)

---

## Requirements
- Python 3.8 or newer
- torch
- psutil

---

## License
MIT License. See [LICENSE](LICENSE).

---

## Keywords
Apple Silicon, MPS, GPU monitor, Mac system monitor, htop alternative, nvitop alternative, terminal monitor, Mac M1, Mac M2, Mac M3, Python process monitor, real-time system stats, minimal system monitor 