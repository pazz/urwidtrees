import urwid
import urwidtrees


tree_widget = urwidtrees.widgets.TreeBox(
    urwidtrees.decoration.CollapsibleIndentedTree(
        urwidtrees.tree.SimpleTree([
            (urwid.SelectableIcon('item 1'), (
                (urwid.SelectableIcon('sub item 1'), None),
                (urwid.SelectableIcon('sub item 2'), None),
            )),
            (urwid.SelectableIcon('item 2'), None),
        ])
    )
)

urwid.MainLoop(tree_widget).run()
