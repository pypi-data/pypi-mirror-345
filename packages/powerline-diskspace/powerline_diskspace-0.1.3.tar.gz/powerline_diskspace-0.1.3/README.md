# Powerline Disk Utilization Indicator

A tiny [Powerline](https://github.com/powerline/powerline) segment I wrote (originally for `tmux`) to show me disk space utilization in its status line. This component does not work natively with `tmux` - if you just want a native tmux-specific component, check out [tmux-df](https://github.com/tassaron/tmux-df).

Here is a screenshot of this segment in action:

![disk utilization example](doc/img/powerline-diskspace-screenshot.png)

The root `/` is red because, unlike `/cache`, it's over the `critical_threshold` I set to 40% for this example.

In this case, the relevant part of the powerline config (`cat ~/.config/powerline/themes/tmux/default.json`) is:

```json
{
"segments": {
  "right": [
    {
      "function": "powerline_diskspace.diskspace.Diskspace",
      "priority": 30,
      "args": {
        "format": "{mounted_on} @ {capacity:.0f}%",
        "mount_ignore_pattern": "(/snap|/dev|/run|/boot|/sys/fs)",
        "show_when_used_over_percent": {
          "/": 20,
        },
        "critical_threshold": 40
      }
    }
  ]
}
}
```

(Other plug-ins featured in the screenshot, like `uptime`, are not shown.)

## Getting Started

System requirements:
 * Linux (macOS support is only partial)
 * Python 3.8+
 * [Powerline](https://github.com/powerline/powerline) set up and in use (code only tested in tmux, but other places like `vim` should work to)

Installation steps:

1. Install the Python package: `pip install powerline-diskspace`.
2. Update your `powerline` (not `tmux`!) config following the example above.
3. Restart the Powerline daemon: `powerline-daemon --replace`

If you have any questions or encounter issues setting up, please don't hesitate to open up an issue on GitHub!


## Customization

There are many ways to customize your output. Please refer to the `__call__` method in `diskspace.py`, which is essentially the "main function" of the segment for more documentation.

## Development

### Testing

1. Create a test environment, e.g., with venv or conda.
2. Ensure `powerline-status` and `pytest` are installed in your test environment.
3. Run `pytest` inside the `powerline_diskspace` folder.

### Deployment

1. Read [the official guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives) to refresh your memory, if needed.
2. `pip install --upgrade build twine`
3. `python3 -m build`
4. `python3 -m twine upload  --verbose dist/*`