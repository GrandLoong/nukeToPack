import os.path as os_path
from nukeToPack import nukeToPack

nuke.pluginAddPath(os_path.join(os_path.dirname(__file__), 'nukeToPack/icons'))
menubar = nuke.menu("Nuke")
toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("VFXPIPELINE", icon="logo.png")
m.addCommand("nukeToPack", "nukeToPack.run()", icon="nukeToPack.png")
