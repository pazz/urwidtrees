"""
Update the tree after it's initially build.

Shows something like:

root                                                                                                                            
|->PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.                                                                             
|  64 bytes from 127.0.0.1: icmp_seq=1 ttl=64 time=0.039 ms                                                                     
|                                                                                                                               
|->64 bytes from 127.0.0.1: icmp_seq=2 ttl=64 time=0.053 ms                                                                     
|                                                                                                                               
|->64 bytes from 127.0.0.1: icmp_seq=3 ttl=64 time=0.064 ms                                                                     

"""
import subprocess
import urwid
import urwidtrees

root_node = [urwid.Text('root'), None]
tree_widget = urwidtrees.widgets.TreeBox(
    urwidtrees.decoration.ArrowTree(
        urwidtrees.tree.SimpleTree([root_node])
    )
)

loop = urwid.MainLoop(tree_widget)


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
