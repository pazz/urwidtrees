import subprocess
import urwid
import urwidtrees

root_node = [urwid.Text('root'), None]
tree_widget = urwidtrees.widgets.TreeBox(
    urwidtrees.decoration.ArrowTree(
        urwidtrees.tree.SimpleTree([root_node])
    )
)

def exit_on_q(key):
    if key in ['q', 'Q']:
        raise urwid.ExitMainLoop()

loop = urwid.MainLoop(tree_widget, 
    unhandled_input=exit_on_q)


def on_stdout(data):
    if not root_node[1]:
        root_node[1] = []
    root_node[1].append((urwid.Text(data), None))
    tree_widget.refresh()


proc = subprocess.Popen(
    ['ping', '127.0.0.1'],
    stdout=loop.watch_pipe(on_stdout),
    close_fds=True)

loop.run()
proc.kill()
