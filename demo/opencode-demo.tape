# Record a real opencode session against the DocCanon README demo project.
#
# The session is genuine: opencode loads the installed DocCanon skill, runs the
# real helper, and reports the stale canonical document and the code file
# responsible. Nothing about the agent or DocCanon is simulated.
#
# Run from the repository root with VHS 0.11.0 (0.12.0 silently writes no
# output; see demo/record_opencode.sh):
#
#     vhs demo/opencode-demo.tape
#
# This produces demo/.build/opencode-session.mp4, which record_opencode.sh
# trims and converts into assets/doccanon-demo.gif.

Output demo/.build/opencode-session.mp4

Set Shell zsh
Set FontFamily "Menlo"
Set FontSize 17
Set LineHeight 1.3
Set Width 1080
Set Height 680
Set Padding 20
Set Margin 0
Set Theme "Dracula"
Set CursorBlink false
Set TypingSpeed 0ms

# Build a governed project where src/auth/session.py changed but its canonical
# owner (docs/features/session.md) did not, then start opencode in it.
Hide
Type "python3 demo/setup_project.py --path /tmp/doccanon-demo-project --stale >/dev/null"
Enter
Sleep 7s
Type "cd /tmp/doccanon-demo-project && clear"
Enter
Sleep 400ms
Show

Type "opencode"
Enter
Sleep 7s
Type "Use DocCanon to check whether the project context is still trustworthy. Be terse: name the stale document and the code file responsible."
Enter

# Give the real session time to run; the recorder is stopped afterwards.
Sleep 100s
