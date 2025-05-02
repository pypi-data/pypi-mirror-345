<h1 align="center">✨ VibeGit ✨</h1>

<p align="center">
Spend more time vibe coding and less time houskeeping your Git repository.
</p>

---

<style>
  table#header-table td {
    border: none;
    margin: 24px 0;
  }
</style>
<table id="header-table">
  <tbody>
    <tr>
      <td><img src="resources/before-vibegit.png"></td>
      <td><img src="resources/after-vibegit.png"></td>
    </tr>
    <tr>
      <td>^ You before using VibeGit</td>
      <td>^ You after using VibeGit</td>
    </tr>
  </tbody>
</table>

---

## Never ever do manual Git housekeeping again

Let's be honest. You know the problem. You spent hours or days working on a feature and forgot to structure and commit changes once in a while. Suddenly you are facing 30 open file changes, scattered across a dozen or so different subtasks.

Now comes the fun part: **Crafting perfect, atomic commits.**

You could:

1.  Spend 20 minutes meticulously using `git add -p`, squinting at diffs like a code archaeologist.
2.  Write a vague commit message like `"fix stuff"` and promise yourself you'll `rebase -i` later (spoiler: you won't).
3.  Just `git commit -a -m "WIP"` and call it a day, leaving a dumpster fire for future you (or your poor colleagues).

**There *has* to be a better way.** (Spoiler: There is. Keep reading.)

## Enter VibeGit: Your AI-Powered Git Housekeeper 🤖🧹

> [!WARNING]
> Brace yourself. What you going to see now might feel like magic.

In your messy Git repository, just hit

```bash
vibegit commit
```

✨ **And it *automagically* groups related changes (hunks) together based on their *semantic meaning*!** ✨

No more manual patch-adding hell. No more "what did I even change here?" moments.

VibeGit analyzes your diff, considers your branch name, peeks at your recent commit history (for stylistic consistency, not blackmail... probably), and then proposes logical, beautifully grouped commits with **AI-generated commit messages**.

## Features That Will Make You Question Reality (or at Least Your Old Workflow)

*   🧠 **Semantic Hunk Grouping:** VibeGit doesn't just look at file names; it looks at *what the code does* to bundle related changes. It's like magic, but with more AI slop.
*   ✍️ **AI-Generated Commit Messages:** Get sensible, well-formatted commit messages suggested for each group. Tweak them or use them as-is. Your commit log will suddenly look respectable.
*   🤖 **Multiple Workflow Modes:**
    *   **YOLO Mode:** Feeling lucky? Automatically apply all of VibeGit's proposals. What could possibly go wrong?
    *   **Interactive Mode:** Review each proposed commit, edit the message in your default editor, and apply them one by one. For the cautious (or skeptical).
    *   **Summary Mode:** Get a quick overview of what VibeGit plans to do before diving in.
*   🚫 **Sanity Check:** Checks whether you didn't accidentally forgot your life pension in the form of a Bitcoin key in your `.env` file. 

## Installation: Get Ready to Vibe

Via pip:

```
pip install vibegit
```

Via pipx:

```
pipx vibegit
```

Via uv:

```
uvx vibegit
```


*(Requirements file TBD, but you get the idea)*

## Usage: Unleash the Vibe

Navigate to your Git repository containing unstaged changes.

```bash
# Run the interactive CLI (assuming it's installed or you use python -m)
python -m vibegit.cli
# Or, if installed as a command:
# vibegit commit
```

## The Future: More Vibes, More Git? 🚀

Right now, VibeGit focuses on `commit`. But the vision is grand! Imagine AI assistance for:

*   `vibegit merge` (Resolving conflicts? Maybe too ambitious...)
*   `vibegit rebase` (Interactive rebasing suggestions?)
*   `vibegit checkout` (Suggesting relevant branches?)

We're aiming to turn this quirky tool into a full-fledged AI Git companion. Maybe even a **commercial service** one day, so get in on the ground floor while it's still just charmingly experimental!

## Contributing (Please Help Us Vibe Better!)

Found a bug? Have a killer feature idea? Did the AI `rm -rf`ed your repository once again?

Open an issue or submit a pull request! We appreciate constructive feedback and contributions. Let's make Git less of a chore, together.

## License

Currently under [Your License Here - e.g., MIT / Apache 2.0 / Proprietary - TBD]. Stay tuned as we figure out our world domination plans.

---

<p align="center">
  <b>Happy Vibing! ✨</b>
</p>
