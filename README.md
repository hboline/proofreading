# proofreading

a TUI written in python for powerful proofreading actions in Adobe Reader.

On macOS, open a PDF in Reader and run `uv run proofread` from your terminal. Allow that
terminal in **System Settings > Privacy & Security > Accessibility** so proofread
can verify window focus and send Copy, Paste, and Save shortcuts.

The macOS controller requests activation and checks the focused app and window
every 20 ms while waiting, with a two-second timeout. It returns as soon as focus
is confirmed and checks again before sending input. It does not poll or reclaim
focus while idle. Shortcuts use native Quartz events with the Command modifier
attached; Windows and Linux continue to use PyAutoGUI with Control.


<div align="center">
  <img width="550" height="1176" alt="image" src="https://github.com/user-attachments/assets/a60067fb-cffb-4ec0-abac-064ddbbeb851" />
</div>
