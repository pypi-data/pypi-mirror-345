import tkinter as tk
from tkinter import simpledialog, messagebox, ttk, scrolledtext
import os
from ugit_module import base, data

# Setup .ugit context as CLI does
from contextlib import contextmanager
@contextmanager
def setup_git_context():
    with data.change_git_dir('.'):
        yield

# --- Function: Init Repo ---
def init_repo():
    git_dir = os.path.join(os.getcwd(), ".ugit")
    if os.path.exists(git_dir):
        msg = "UGit repo already initialized."
        print(msg)
        messagebox.showinfo("Already Initialized", msg)
        return
    with setup_git_context():
        base.init()
    msg = "UGit repository initialized successfully."
    print(msg)
    messagebox.showinfo("Initialized", msg)

# --- Function: Commit ---
def commit():
    msg = simpledialog.askstring("Commit", "Enter commit message:")
    if msg:
        with setup_git_context():
            oid = base.commit(msg)
        print(f"Committed: {oid}")
        messagebox.showinfo("Commit", f"Committed: {oid}")

# --- Function: Create Tag ---
def create_tag():
    tag = simpledialog.askstring("Tag", "Enter tag name (e.g., v1.0):")
    if tag:
        with setup_git_context():
            head_oid = base.get_oid('@')
            base.create_tag(tag, head_oid)
        print(f"Tag '{tag}' created for commit {head_oid}")
        messagebox.showinfo("Tag Created", f"Tag '{tag}' -> {head_oid}")

# --- Function: View Log ---
def view_log():
    with setup_git_context():
        refs = {}
        for refname, ref in data.iter_refs():
            refs.setdefault(ref.value, []).append(refname)

        output = ""
        for oid in base.iter_commits_and_parents({base.get_oid('@')}):
            commit = base.get_commit(oid)
            ref_names = refs.get(oid, [])
            ref_str = f" ({', '.join(ref_names)})" if ref_names else ''
            output += f"commit {oid[:10]}{ref_str}\n"
            output += f"    {commit.message}\n\n"

        log_output.delete("1.0", tk.END)
        log_output.insert(tk.END, output)
        print("==== UGit Log ====")
        print(output)

# --- Function: Show Branches ---
def show_branches():
    with setup_git_context():
        current_branch = base.get_branch_name()
        branches = list(base.iter_branch_names())
    branch_output.delete("1.0", tk.END)
    print("Branches:")
    for branch in branches:
        prefix = "*" if branch == current_branch else " "
        line = f"{prefix} {branch}"
        print(line)
        branch_output.insert(tk.END, line + "\n")

# --- Function: Create Branch ---
def create_branch():
    name = simpledialog.askstring("New Branch", "Enter branch name:")
    if not name:
        return
    with setup_git_context():
        oid = base.get_oid('@')
        base.create_branch(name, oid)
    msg = f"Branch '{name}' created at {oid[:10]}"
    print(msg)
    messagebox.showinfo("Branch Created", msg)
    show_branches()

# --- Function: Checkout ---
def checkout_version():
    target = simpledialog.askstring("Checkout", "Enter branch or commit to checkout:")
    if not target:
        return
    with setup_git_context():
        try:
            base.checkout(target)
            msg = f"Checked out: {target}"
            print(msg)
            messagebox.showinfo("Checkout", msg)
        except Exception as e:
            print(f"Checkout failed: {e}")
            messagebox.showerror("Checkout Error", str(e))

# --- Function: Merge ---
def merge_commit():
    commit = simpledialog.askstring("Merge", "Enter commit or branch to merge:")
    if not commit:
        return
    with setup_git_context():
        try:
            base.merge(base.get_oid(commit))
            msg = f"Merged '{commit}' into current branch. Please commit."
            print(msg)
            messagebox.showinfo("Merge", msg)
        except Exception as e:
            print(f"Merge failed: {e}")
            messagebox.showerror("Merge Error", str(e))

# ---- GUI SETUP ----
root = tk.Tk()
root.title("UGit - Version Control GUI")
root.geometry("520x520")

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True)

# --- Tab: UGit Controls ---
tab_controls = ttk.Frame(notebook)
notebook.add(tab_controls, text="UGit Controls")

tk.Button(tab_controls, text="Init Repository", width=40, command=init_repo).pack(pady=5)
tk.Button(tab_controls, text="Commit", width=40, command=commit).pack(pady=5)
tk.Button(tab_controls, text="Create Tag", width=40, command=create_tag).pack(pady=5)
tk.Button(tab_controls, text="View Log", width=40, command=view_log).pack(pady=5)

log_output = scrolledtext.ScrolledText(tab_controls, wrap=tk.WORD, width=60, height=15)
log_output.pack(padx=10, pady=10)

# --- Tab: Branch ---
tab_branch = ttk.Frame(notebook)
notebook.add(tab_branch, text="Branch")

branch_output = scrolledtext.ScrolledText(tab_branch, wrap=tk.WORD, width=60, height=15)
branch_output.pack(padx=10, pady=(10, 5))

tk.Button(tab_branch, text="Show Branches", width=40, command=show_branches).pack(pady=5)
tk.Button(tab_branch, text="Create New Branch", width=40, command=create_branch).pack(pady=5)

# --- Tab: Checkout & Merge ---
tab_checkout = ttk.Frame(notebook)
notebook.add(tab_checkout, text="Checkout & Merge")

tk.Button(tab_checkout, text="Checkout Version/Branch", width=40, command=checkout_version).pack(pady=10)
tk.Button(tab_checkout, text="Merge Commit/Branch", width=40, command=merge_commit).pack(pady=10)

# Start GUI
root.mainloop()
