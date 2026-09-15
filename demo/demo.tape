# Paced README walkthrough for DocCanon.
#
# This is not a raw agent session: every status, diff, and finding shown here is
# printed by the real DocCanon helper running against a governed project. The
# only authored frames are the three cards in demo/card.py, which frame the
# story. Pacing is deliberate -- each key result is held long enough to read.
#
# demo/record.sh substitutes __REPO__ and __DEMO_PATH__ and records this tape
# with VHS 0.11.0 (0.12.0 silently writes no output). It then converts the MP4
# into the looping assets/doccanon-demo.gif.

Output demo/.build/doccanon-demo.mp4

Set Shell zsh
Set FontFamily "Menlo"
Set FontSize 18
Set LineHeight 1.35
Set Width 1200
Set Height 640
Set Padding 24
Set Margin 0
Set Theme "Dracula"
Set CursorBlink false

# 1. Title card
Set TypingSpeed 0ms
Hide
Type "cd __DEMO_PATH__ && alias c='python3 .card.py'"
Enter
Type "clear && c title"
Enter
Sleep 400ms
Show
Sleep 2.2s

# 2. The governed project map lives beside the code
Set TypingSpeed 0ms
Hide
Type "clear && c caption 'the project map lives beside the code'"
Enter
Sleep 200ms
Show
Set TypingSpeed 10ms
Type "git ls-files CONTEXT.md docs src"
Enter
Sleep 2s

# 3. The baseline is verified against the code
Set TypingSpeed 0ms
Hide
Type "clear && c caption 'context is verified against the code'"
Enter
Sleep 200ms
Show
Set TypingSpeed 10ms
Type "python3 .agents/skills/doccanon/scripts/doccanon.py check | grep -E 'DocCanon|maturity'"
Enter
Sleep 3.4s

# 4. Code changes, its canonical owner does not
Set TypingSpeed 0ms
Hide
Type "python3 __REPO__/demo/prepare.py --drift --path __DEMO_PATH__"
Enter
Sleep 700ms
Type "clear && c caption 'code changes. its canonical owner does not.'"
Enter
Sleep 200ms
Show
Set TypingSpeed 10ms
Type "git diff --cached src/session.py"
Enter
Sleep 3s

# 5. DocCanon refuses to treat the stale state as synchronized
Set TypingSpeed 0ms
Hide
Type "clear && c caption 'DocCanon refuses to call it synchronized'"
Enter
Sleep 200ms
Show
Set TypingSpeed 10ms
Type "python3 .agents/skills/doccanon/scripts/doccanon.py check --staged | grep -E 'DocCanon|ERROR'"
Enter
Sleep 5s

# 6. Closing card
Set TypingSpeed 0ms
Hide
Type "clear && c closing"
Enter
Sleep 300ms
Show
Sleep 2.4s
