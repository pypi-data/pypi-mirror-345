<file name=0 path=/home/nhomar/Source/macrokeyd/README.md># macrokeyd

`macrokeyd` is a Python daemon that allows assigning custom actions to a specific keyboard, such as commands, text, system shortcuts, or chained sequences. It is designed to run as a `systemd` service and configured through modular JSON files.

---

## 🚀 Quick Installation from PyPI

```bash
pip install macrokeyd
```

> Requires Python >= 3.7 and Linux with `evdev` support.

---

## 🧪 Testing Installation

```bash
macrokeyd --help
macrokeyd --version
```

You can start the daemon with:

```bash
macrokeyd --run
```

> By default, it searches for `~/.local/share/macrokeyd/default.json` and creates it if it doesn't exist.

---

## ⚙️ Installing as a systemd service

```bash
macrokeyd-install-service
```

Check the status:

```bash
systemctl status macrokeyd
```

Uninstall:

```bash
macrokeyd-uninstall-service
```

### 📌 Installation with System Python (Recommended for Gtk Integration)

If you're using Gtk integration (such as PyGObject), it's recommended to use the system Python to avoid compatibility issues:

```bash
sudo apt install python3 python3-pip python3-venv python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
```

> Also, install Tkinter for MouseInfo support, which requires system-level libraries:

```bash
sudo apt install python3-tk python3-dev
```

```bash
pyenv virtualenv --system-site-packages system macrokeyd-env
pyenv local macrokeyd-env
pip install macrokeyd
```

Verify the installation:

```bash
python -c "import gi; print(gi.__file__)"
```

The output should resemble:

```
/usr/lib/python3/dist-packages/gi/__init__.py
```

---

## 🎛️ Macro Configuration

The configuration file is located at (or created at):

```
~/.local/share/macrokeyd/default.json
```

Example content:

```json
{
  "meta": {
    "target_device_name": "TEC-FX556K"
  },
  "macros": {
    "KEY_Q": {"action": "command", "value": "gnome-terminal"},
    "KEY_W": {"action": "text", "value": "Hello world"}
  }
}
```

---

## 🧱 Local Development

```bash
git clone https://gitlab.com/your_user/macrokeyd.git
cd macrokeyd
make install
```

---

## 🛠 Useful Commands (`make`)

- `make build` → generates `.whl` and `.tar.gz` packages
- `make install` → installs locally with `--force-reinstall`
- `make clean` → cleans up artifacts
- `make release LEVEL=patch` → bumps version and pushes
- `make release-changelog` → same as `release` and updates `CHANGELOG.md`
- `make release-pypi` → publishes to PyPI
- `make release-test` → publishes to TestPyPI

---

## 📦 Publishing to PyPI

Check [RELEASE.md](./RELEASE.md) for the full versioning and release cycle details.</file>